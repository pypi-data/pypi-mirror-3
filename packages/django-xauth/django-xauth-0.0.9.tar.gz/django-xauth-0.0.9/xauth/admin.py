from django.contrib import admin

from xauth.models import XauthAssociation

class XauthAssociationAdmin(admin.ModelAdmin):
    list_display = ['identity', 'user', 'service']
    list_filter = ['service']
    search_fields = ['identity', 'user__username']

admin.site.register(XauthAssociation, XauthAssociationAdmin)
