from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('xauth.urls')),
    url(r'^$', direct_to_template, {'template': 'index.html'}),
    url(r'^welcome', direct_to_template, {'template': 'welcome.html'}),
)
