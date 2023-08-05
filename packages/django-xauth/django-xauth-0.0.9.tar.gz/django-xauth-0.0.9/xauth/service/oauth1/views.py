from __future__ import absolute_import
import oauth2
import cgi
import urllib
import time

import logging

from django.shortcuts import render, redirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _

from xauth.util import absolute_url
from xauth.service.oauth1.settings import PROVIDERS

logger = logging.getLogger('xauth.service.xauth.views')

def get_setting(provider, key):
    if key in ['request_token_url', 'access_token_url', 'authenticate_url']:
        return PROVIDERS[provider][key]
    else:
        return getattr(settings, 'XAUTH_OAUTH1_%s_%s' % (provider.upper(), key.upper()))

def prepare(request):
    """
    Receive request token.
    """

    logger.debug('VIEW_START prepare')

    provider = request.GET.get('provider')
    logger.debug('%s provider choosed' % provider)

    if not provider in PROVIDERS:
        messages.error(request, u'Invalid request')
        return redirect('xauth_login')

    consumer = oauth2.Consumer(get_setting(provider, 'consumer_key'),
                          get_setting(provider, 'consumer_secret'))
    client = oauth2.Client(consumer)

    sid = str(time.time())
    return_to = absolute_url(reverse('xauth_exec', args=['oauth1', 'finish']) + '?sid=%s' % sid)
    request_url = get_setting(provider, 'request_token_url') + '?oauth_callback=%s' % urllib.quote(return_to)
    resp, content = client.request(request_url, 'GET')
    if resp['status'] != '200':
        messages.error(request, u'Invalid response from oauth provider [code=%s]' % resp['status'])
        logging.error('Invalid response from oauth provider with code %s' % resp['status'])
        logging.error(u'[start]%s[end]' % content)
        return redirect('xauth_login')
    else:
        oauth_state = dict(cgi.parse_qsl(content))
        oauth_state['provider'] = provider
        request.session['xauth_oauth_%s' % sid] = oauth_state

        return redirect('%s?oauth_token=%s' % (
            get_setting(provider, 'authenticate_url'),
            oauth_state['oauth_token'])) 


def finish(request):
    """
    Finish the oauth authentication process.
    """

    logger.debug('VIEW START finish')

    sid = request.GET.get('sid')
    oauth_state = request.session.get('xauth_oauth_%s' % sid)
    if not oauth_state:
        messages.error(request, u'Invalid authentication data')
        return redirect('xauth_login')
    provider = oauth_state['provider']

    token = oauth2.Token(
        oauth_state['oauth_token'],
        oauth_state['oauth_token_secret'])
    consumer = oauth2.Consumer(get_setting(provider, 'consumer_key'),
                          get_setting(provider, 'consumer_secret'))
    client = oauth2.Client(consumer, token)

    resp, content = client.request(get_setting(provider, 'access_token_url'), 'GET')
    if resp['status'] != '200':
        messages.error(request, u'Invalid response from oauth provider [code=%s]' % resp['status'])
        logging.error('Invalid response from oauth provider with code %s' % resp['status'])
        logging.error(u'[start]%s[end]' % content)
        return redirect('xauth_login')

    response = dict(cgi.parse_qsl(content))
    profile = {'nickname': response['screen_name']}
    identity = 'http://twitter.com/%s' % response['screen_name']

    request.session['xauth_response'] = {
        'identity': identity,
        'service': 'oauth1',
        'profile': profile,
    }

    return redirect('xauth_complete')
