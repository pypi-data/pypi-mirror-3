import logging

from django.contrib.auth.models import User

from xauth.models import XauthAssociation

logger = logging.getLogger('xauth.backends')

class XauthBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = True
    supports_inactive_user = True

    def authenticate(self, xauth_response):
        logger.debug('Authenticating user with %s xauth service' % xauth_response['service'])

        try:
            assoc = XauthAssociation.objects.get(identity=xauth_response['identity'])
        except XauthAssociation.DoesNotExist:
            return None
        else:
            return assoc.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
