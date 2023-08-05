from __future__ import absolute_import
import re

import logging
from openid.consumer import consumer
from openid import oidutil
from openid.extensions import ax, sreg
from openid.consumer.discover import DiscoveryFailure

from django.shortcuts import render, redirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _

from xauth.util import absolute_url
from xauth.service.openid.profile import add_profile_query, process_profile_data

logger = logging.getLogger('xauth.service.openid.views')

def logging_handler(message):
    logger.debug('OPENID LIB: %s' % message)

oidutil.log = logging_handler

def get_consumer(request):
      "Get a Consumer object to perform OpenID authentication."

      logger.debug('Setting up the consumer')
      return consumer.Consumer(request.session, None)#get_store())


def prepare(request):
    """
    Make OpenID authentication request.

    More verbosly:
     * Accept User-Supplied Identifier
     * Make its normalization/discoverying
     * Build authentication request
     * Reidrect user to OpenID provider
    """

    logger.debug('VIEW_START prepare')

    openid_url = request.GET.get('openid_url')
    if not openid_url:
        messages.error(request, u'Invalid openid URL')
        return redirect('xauth_login')

    logger.debug('Processing %s OpenID URL' % openid_url)
    con = get_consumer(request)

    try:
        auth_request = con.begin(openid_url)
    except DiscoveryFailure, ex:
        logger.error('DiscoveryFailure', exc_info=ex)
        messages.error(request, _('OpenID discovery error: %s' % ex))
        return redirect('xauth_login')
    else:
        add_profile_query(auth_request, settings.XAUTH_PROFILE_FIELDS)

        # Compute the trust root and return URL values to build the
        # redirect information.
        trust_root = absolute_url('')
        return_to = absolute_url(reverse('xauth_exec', args=['openid', 'finish']))

        # Send the browser to the server either by sending a redirect
        # URL or by generating a POST form.
        if auth_request.shouldSendRedirect():
            return redirect(auth_request.redirectURL(trust_root, return_to))
        else:
            # Beware: this renders a template whose content is a form
            # and some javascript to submit it upon page load.  Non-JS
            # users will have to click the form submit button to
            # initiate OpenID authentication.
            form_html = auth_request.formMarkup(
                trust_root, return_to, False, {'id': 'openid_message'})
            context = {'html': form_html}
            return render(request, 'xauth/openid/request_form.html', context)

    assert False


def finish(request):
    """
    Finish the OpenID authentication process.
    
    Invoke the OpenID library with the response from the OpenID server and render a page
    detailing the result.
    """

    logger.debug('VIEW START finish')

    result = {}

    # Because the object containing the query parameters is a
    # MultiValueDict and the OpenID library doesn't allow that, we'll
    # convert it to a normal dict.
    request_args = dict(request.GET.items())

    # OpenID 2 can send arguments as either POST body or GET query
    # parameters.
    if request.method == 'POST':
        request_args.update(dict(request.POST.items()))

    logger.debug('Arguments: %s' % '\n'.join('%s: %s' % x for x in request_args.items()))

    if request_args:
        con = get_consumer(request)

        # Get a response object indicating the result of the OpenID
        # protocol.
        return_to = absolute_url(reverse('xauth_exec', args=['openid', 'finish']))
        logger.debug('Setting up the OpenID response object')
        response = con.complete(request_args, return_to)


        if response.status == consumer.SUCCESS:
            profile = process_profile_data(response, settings.XAUTH_PROFILE_FIELDS)

            identity = response.identity_url
            request.session['xauth_response'] = {
                'service': 'openid',
                #'response': response,
                'identity': identity,
                'profile': profile,
                #{'url': response.getDisplayIdentifier(),
            }
            return redirect('xauth_complete')
        else:
            if response.status == consumer.CANCEL:
                messages.error(request, _('Authentication cancelled'))
            elif response.status == consumer.FAILURE:
                messages.error(request, _('OpenID authentication failure: %s' % response.message))
            else:
                messages.error(request, _('Unknown OpenID response type: %s' % response.status))
            return redirect('xauth_login')
    else:
        messages.error(request, u'Invalid openid data')
        return redirect('xauth_login')
