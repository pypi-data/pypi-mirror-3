from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from xauth.models import XauthAssociation

class Command(BaseCommand):
    args = '<appname>'
    help = 'Import identities from other authentication application'

    def handle(self, *args, **options):
        if not len(args):
            raise CommandError('appname is required')
        
        cursor = connection.cursor()
        appname = args[0]
        if appname == 'publicauth':
            cursor.execute("SELECT user_id, identity, provider "
                           "FROM publicauth_publicid")
            for uid, identity, provider in cursor.fetchall():
                if provider in ['openid', 'google']:
                    self.save_association(uid, identity, 'openid')
                else:
                    print 'Uknown provider: %s' % provider

    def save_association(self, uid, identity, service):
        obj, new = XauthAssociation.objects.get_or_create(
            user_id=uid, identity=identity, service=service)
        if new:
            print u'New association: %s <-[%s]-> %s' % (obj.user, service, obj.identity)
        else:
            print u'Association already exists: %s <-[%s]-> %s' % (obj.user, service, obj.identity)
        
