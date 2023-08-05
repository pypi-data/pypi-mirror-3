from django.conf.urls.defaults import *

urlpatterns = patterns('xauth.views',
    url(r'^$', 'xauth_login', name='xauth_login'),
    url(r'^prepare/(\w+)$', 'xauth_prepare', name='xauth_prepare'),
    url(r'^exec/(\w+)/(\w+)$', 'xauth_exec', name='xauth_exec'),
    url(r'^complete$', 'xauth_complete', name='xauth_complete'),
    url(r'^logout$', 'xauth_logout', name='xauth_logout'),
    url(r'^identity$', 'xauth_identity_list', name='xauth_identity_list'),

    # Special cases for simple backend
    url(r'^login$', 'xauth_exec', {'service': 'simple', 'command': 'simple_login'}, name='xauth_simple_login'),
    url(r'^signup$', 'xauth_exec', {'service': 'simple', 'command': 'simple_signup'}, name='xauth_simple_signup'),
)
