import logging

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib import auth
from django.utils.http import urlquote
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from xauth.forms import AccountForm
from xauth.models import XauthAssociation
from xauth.util import import_path, get_redirect_url

logger = logging.getLogger('xauth.views')

def clear_xauth_session(request):
    "Remove from the session result of recent xauth activity."

    try:
        del request.session['xauth_response']
    except KeyError:
        pass


def xauth_login(request):
    "Display initial Log In page."

    logger.debug('VIEW START xauth_login')

    # Remember the URL to which user should be
    # redirected after successful logging in
    request.session['xauth_redirect_url'] = request.GET.get('next')
    return render(request, 'xauth/login.html')

def xauth_prepare(request, service):
    "First step of authentication."

    logger.debug('VIEW START prepare [service=%s]' % service)
    return xauth_exec(request, service, 'prepare')


def xauth_exec(request, service, command):
    "Execute the view of specified service."

    logger.debug('VIEW START exec [service=%s, command=%s]' % (service, command))
    if not service in settings.XAUTH_SERVICES:
        messages.error(request, u'Invalid xauth service: %s' % service)
        return redirect('xauth_login')
    module = __import__('xauth.service.%s.views' % service, globals(), locals(), ['foo'])
    return getattr(module, command)(request)


def xauth_complete(request):
    """
    Final step of authentication
   
    If user is alreay authenticated then just create new association
    else show profile form with username and email fields (could be customized).
    """

    if not 'xauth_response' in request.session:
        messages.error(request, _('Invalid authentication data'))
        return redirect('xauth_login')
    user = auth.authenticate(xauth_response=request.session['xauth_response'])
    if user:
        if user.is_active:
            auth.login(request, user)
            messages.success(request, _('You have successfully logged in'))
            clear_xauth_session(request)
            return redirect(get_redirect_url(request, settings.XAUTH_SIGNIN_SUCCESS_URL))
        else:
            message.error(request, _('Your account is disabled'))
            # We should reconstruct `next` argument
            # to allow user to try another account
            if request.session.get('xauth_redirect_url'):
                qs = '?next=%s' % urlquote(request.session.get('xauth_redirect_url'))
            else:
                qs = ''
            clear_xauth_session(request)
            return redirect(reverse('xauth_login') + qs)
    else:
        xresponse = request.session['xauth_response']
        service = xresponse['service']

        if request.user.is_authenticated():
            XauthAssociation.objects.create(user=request.user, identity=xresponse['identity'],
                                            service=service)
            messages.success(request, _('You have successfully created new association'))
            clear_xauth_session(request)
            return redirect(get_redirect_url(request, settings.XAUTH_SIGNUP_SUCCESS_URL))

        user = User(is_active=True)
        form_class = import_path(settings.XAUTH_ACCOUNT_FORM)
        form = form_class(request.POST or None, instance=user, initial=request.session['xauth_response']['profile'])
        if form.is_valid():
            user = form.save()
            XauthAssociation.objects.create(user=user, identity=xresponse['identity'],
                                            service=service)
            messages.success(request, _('You have been successfuly signed up'))
            # Need to assign `backend` attribute to the user
            user = auth.authenticate(xauth_response=request.session['xauth_response'])
            auth.login(request, user)
            clear_xauth_session(request)
            return redirect(get_redirect_url(request, settings.XAUTH_SIGNUP_SUCCESS_URL))
        else:
            context = {'form': form,}
            return render(request, 'xauth/profile.html', context)


def xauth_logout(request):
    auth.logout(request)
    messages.success(request, _('You have successuly logged out'))
    return redirect(settings.XAUTH_LOGOUT_URL)


@login_required
def xauth_identity_list(request):
    idents = XauthAssociation.objects.filter(user=request.user)
    return render(request, 'xauth/identity_list.html', {'idents': idents})
