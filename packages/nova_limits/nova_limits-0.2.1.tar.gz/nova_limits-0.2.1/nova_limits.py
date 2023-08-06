# Copyright 2012 Rackspace
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import time

from nova.api.openstack import wsgi

from turnstile import limits
from turnstile import middleware


def nova_preprocess(midware, environ):
    """
    Pre-process requests to nova.  The tenant name is extracted from
    the nova context, and the applicable rate limit class is looked up
    in the database.  Both pieces of data are attached to the request
    environment.  This preprocessor must be present to use the
    NovaClassLimit rate limiting class.
    """

    # First, figure out the tenant
    context = environ.get('nova.context')
    if context:
        tenant = context.project_id
    else:
        # There *should* be a tenant by now, but let's be liberal
        # in what we accept
        tenant = '<NONE>'
    environ['turnstile.nova.tenant'] = tenant

    # Now, figure out the rate limit class
    klass = midware.db.get('limit-class:%s' % tenant) or 'default'
    klass = environ.setdefault('turnstile.nova.limitclass', klass)

    # Finally, translate Turnstile limits into Nova limits, so we can
    # use Nova's /limits endpoint
    limits = []
    for turns_lim in midware.limits:
        # If the limit has a rate_class, ensure it equals the
        # appropriate one for the user.  If the limit does not have a
        # rate_class, we want to include it in the final list.
        if getattr(turns_lim, 'rate_class', klass) != klass:
            continue

        # Translate some information squirreled away in the limit
        verbs = turns_lim.verbs or ['GET', 'HEAD', 'POST', 'PUT', 'DELETE']
        unit = turns_lim.unit.upper()
        if unit.isdigit():
            unit = 'UNKNOWN'

        # Now, build a representation of the limit
        for verb in verbs:
            limits.append(dict(
                    verb=verb,
                    URI=turns_lim.uri,
                    regex=turns_lim.uri,
                    value=turns_lim.value,
                    unit=unit,

                    # We simply don't have enough information
                    # available to determine these values, because it
                    # depends on exactly which URL was requested.  We
                    # therefore fall back to using wide-open values.
                    remaining=turns_lim.value,
                    resetTime=time.time(),
                    ))

    # Save the limits for Nova to use
    environ['nova.limits'] = limits


class NovaClassLimit(limits.Limit):
    """
    Rate limiting class for applying rate limits to classes of Nova
    tenants.  The nova_limits:nova_preprocess preprocessor must be
    configured for this limit class to match.
    """

    attrs = dict(
        rate_class=dict(
            desc=('The rate limiting class this limit applies to.  Required.'),
            type=str,
            ),
        )

    def route(self, uri, route_args):
        """
        Filter version identifiers off of the URI.
        """

        if uri.startswith('/v1.1/'):
            return uri[5:]
        elif uri.startswith('/v2/'):
            return uri[3:]

        return uri

    def filter(self, environ, params, unused):
        """
        Determines whether this limit applies to this request and
        attaches the tenant name to the params.
        """

        # Do we match?
        if ('turnstile.nova.limitclass' not in environ or
            self.rate_class != environ['turnstile.nova.limitclass']):
            raise limits.DeferLimit()

        # OK, add the tenant to the params
        params['tenant'] = environ['turnstile.nova.tenant']


class NovaTurnstileMiddleware(middleware.TurnstileMiddleware):
    """
    Subclass of TurnstileMiddleware.

    This version of TurnstileMiddleware overrides the format_delay()
    method to utilize Nova's OverLimitFault.
    """

    def format_delay(self, delay, limit, bucket, environ, start_response):
        """
        Formats the over-limit response for the request.  This variant
        utilizes Nova's OverLimitFault for consistency with Nova's
        rate-limiting.
        """

        # Build the error message based on the limit's values
        args = dict(
            value=limit.value,
            verb=environ['REQUEST_METHOD'],
            uri=limit.uri,
            unit_string=limit.unit.upper(),
            )
        error = _("Only %(value)s %(verb)s request(s) can be "
                  "made to %(uri)s every %(unit_string)s.") % args

        # Set up the rest of the arguments for wsgi.OverLimitFault
        msg = _("This request was rate-limited.")
        retry = time.time() + delay

        # Convert to a fault class
        fault = wsgi.OverLimitFault(msg, error, retry)

        # Now let's call it and return the result
        return fault(environ, start_response)
