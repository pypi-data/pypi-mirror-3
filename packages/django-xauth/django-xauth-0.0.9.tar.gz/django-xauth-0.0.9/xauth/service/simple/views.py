from __future__ import absolute_import
import logging

from django.shortcuts import render, redirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib import auth
from django.template.loader import render_to_string
from django.core.mail import send_mail

from urlauth.util import wrap_url

from xauth.util import absolute_url, get_redirect_url, import_path
from xauth.service.simple.forms import LoginForm

logger = logging.getLogger('xauth.service.xauth.simple')


if hasattr(settings, 'XAUTH_SIMPLE_SIGNUP_FORM'):
    SignupForm = import_path(settings.XAUTH_SIMPLE_SIGNUP_FORM)
else:
    if settings.XAUTH_SIMPLE_SIGNUP_METHOD == 'username':
        SignupForm = import_path('xauth.service.simple.forms.UsernameSignupForm')
    elif settings.XAUTH_SIMPLE_SIGNUP_METHOD == 'email':
        SignupForm = import_path('xauth.service.simple.forms.EmailSignupForm')
    else:
        raise Exception('Unknown signup method: %s' % settings.XAUTH_SIMPLE_METHOD)


def simple_login(request):
    form = LoginForm(request.POST or None)

    # Remember the URL to which user should be
    # redirected after successful logging in
    if 'next' in request.GET:
        request.session['xauth_redirect_url'] = request.GET['next']

    if form.is_valid():
        user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        auth.login(request, user)
        messages.success(request, _('You have successfully logged in'))
        return redirect(get_redirect_url(request, settings.XAUTH_SIGNIN_SUCCESS_URL))
    context = {'form': form,}
    return render(request, 'xauth/simple/login.html', context)


def simple_signup(request):
    form = SignupForm(request.POST or None)

    # Remember the URL to which user should be
    # redirected after successful logging in
    if 'next' in request.GET:
        request.session['xauth_redirect_url'] = request.GET['next']

    if form.is_valid():
        user = form.save()
        if settings.XAUTH_ACTIVATION_REQUIRED:
            user.is_active = False
            user.save()
            url = absolute_url(reverse('xauth_exec', args=['simple', 'activation']))
            url = wrap_url(url, uid=user.id)
            context = {
                'hostname': settings.XAUTH_HOSTNAME,
                'user': user,
                'url': url,
                'password': form.cleaned_data['password'],
            }
            subject = _('Activation Required')
            body = render_to_string('xauth/simple/activation_email.txt', context)
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            return redirect('xauth_exec', 'simple', 'activation_required')
        else:
            user = auth.authenticate(username=user.username, password=form.cleaned_data['password'])
            auth.login(request, user)

            context = {
                'hostname': settings.XAUTH_HOSTNAME,
                'user': user,
                'password': form.cleaned_data['password'],
            }
            subject = _('Signup Complete')
            body = render_to_string('xauth/simple/signup_complete.txt', context)
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            messages.success(request, _('You have been successfuly signed up'))
            return redirect(get_redirect_url(request, settings.XAUTH_SIGNUP_SUCCESS_URL))

    context = {'form': form}
    return render(request, 'xauth/simple/signup.html', context)


def activation_required(request):
    return render(request, 'xauth/simple/activation_required.html')


def activation(request):
    if hasattr(request, 'authkey'):
        messages.success(request, _('You have successfully activated your account'))
        user = request.authkey.get_user()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth.login(request, user)    
        return redirect(get_redirect_url(request, settings.XAUTH_SIGNUP_SUCCESS_URL))
    else:
        messages.error(request, _('Your activation key is invalid'))
        return redirect('xauth_simple_signup')


