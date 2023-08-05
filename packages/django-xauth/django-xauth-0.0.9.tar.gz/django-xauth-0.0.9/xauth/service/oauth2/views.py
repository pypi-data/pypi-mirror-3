from __future__ import absolute_import
import cgi
import urllib
import time
from tyoi.oauth2 import AccessTokenRequest, AccessTokenRequestError, AccessTokenResponseError
from tyoi.oauth2.grants import AuthorizationCode
from tyoi.oauth2.authenticators import ClientPassword

import logging

from django.shortcuts import render, redirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils import simplejson

from xauth.util import absolute_url
from xauth.service.oauth2.settings import PROVIDERS

logger = logging.getLogger('xauth.service.xauth.views')

def get_setting(provider, key):
    if key in ['authenticate_url', 'access_token_url']:
        return PROVIDERS[provider][key]
    else:
        return getattr(settings, 'XAUTH_OAUTH2_%s_%s' % (provider.upper(), key.upper()))

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


    sid = str(time.time())
    oauth_state = {'provider': provider}
    request.session['xauth_oauth_%s' % sid] = oauth_state
    return_to = absolute_url(reverse('xauth_exec', args=['oauth2', 'finish']) + '?sid=%s' % sid)

    auth_uri = AuthorizationCode.build_auth_uri(
        get_setting(provider, 'authenticate_url'),
        get_setting(provider, 'client_id'),
        #scope=['email', 'user_birthday'],
        redirect_uri=return_to)
    return redirect(auth_uri)


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

    if not 'code' in request.GET:
        message.error(request, u'Invalid oauth response')
        return redirect('xauth_login')

    return_to = absolute_url(reverse('xauth_exec', args=['oauth2', 'finish']) + '?sid=%s' % sid)
    grant = AuthorizationCode(request.GET['code'], return_to)
    authenticator = ClientPassword(
        get_setting(provider, 'client_id'),
        get_setting(provider, 'client_secret'))
    oauth_request = AccessTokenRequest(authenticator, grant,
        get_setting(provider, 'access_token_url'))

    if provider in 'facebook':
        response_decoder = lambda x: dict(cgi.parse_qsl(x))
    else:
        response_decoder = None

    try:
        token = oauth_request.send(response_decoder)
    except AccessTokenRequestError, ex:
        messages.error(request, u'Invalid response from oauth provider [code=%s]' % ex.error_code)
        logging.error('Invalid response from oauth provider [code=%s]' % ex.error_code)
        logging.error(u'[start]%s[end]' % (ex.error_description or ex.error_code_description))
        return redirect('xauth_login')
    except AccessTokenResponseError, ex:
        messages.error(request, u'Invalid response from oauth provider: %s' % ex.message)
        logging.error('Invalid response from oauth provider: %s' % ex.message)
        return redirect('xauth_login')
    except Exception:
        messages.error(request, u'Oauth Error')
        logging.error('Error')
        return redirect('xauth_login')

    profile = {}

    if provider == 'facebook':
        # http://developers.facebook.com/docs/reference/api/user/
        try:
            response = simplejson.loads(urllib.urlopen('https://graph.facebook.com/me?access_token=%s' % token.access_token).read())
        except Exception, ex:
            messages.error(request, u'Error while getting profile details')
            logging.error(u'Error while getting profile details')
            return redirect('xauth_login')


        #PROFILE_KEYS = [
            #'nickname', 'email', 'fullname', 'dob', 'sex',
            #'postcode', 'country', 'language', 'timezone',
        #]
        profile = {
            'nickname': response.get('username', ''),
            'email': response.get('email', ''),
            'fullname': ' '.join([response.get('first_name', ''),
                                 response.get('last_name', '')]).strip(),
            'dob': response.get('birthday', ''),
            'sex': response.get('gender', ''),
            'timezone': response.get('timezone', ''),
        }
        identity = 'http://facebook.com/%s' % (response.get('username') or response['id'])

    if provider == 'vkontakte':
        # http://vkontakte.ru/developers.php?o=-17680044&p=getUserInfoEx
        try:
            response = simplejson.loads(urllib.urlopen('https://api.vk.com/method/getUserInfoEx?access_token=%s' % token.access_token).read())['response']
        except Exception, ex:
            messages.error(request, u'Error while getting profile details')
            logging.error(u'Error while getting profile details')
            return redirect('xauth_login')

        profile = {
            'nickname': response.get('user_id', ''),
            #'email': response.get('email', ''),
            'fullname': response.get('user_name', ''),
            'dob': response.get('user_bdate', ''),
            'sex': response.get('user_sex', ''),
        }
        identity = 'http://vk.com/%s' % response['user_id']

    request.session['xauth_response'] = {
        'identity': identity,
        'service': 'oauth2',
        'profile': profile,
    }

    return redirect('xauth_complete')
