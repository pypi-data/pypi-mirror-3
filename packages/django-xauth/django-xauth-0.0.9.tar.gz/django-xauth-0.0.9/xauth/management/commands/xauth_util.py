from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = '<service> <command>'
    help = 'Run service specific command'

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError('Usage: xauth %s' % self.args)

        service, command = args[:2]

        module_path = 'xauth.service.%s.commands' % service
        try:
            mod = __import__(module_path, globals(), locals(), ['foo'])
        except ImportError:
            raise CommandError('Could not import %s' % module_path)

        command_path = 'xauth.service.%s.commands.%s' % (service, command)
        try:
            mod = __import__(command_path, globals(), locals(), ['foo'])
        except ImportError:
            raise CommandError('Could not import %s' % command_path)

        getattr(mod, 'handle')(args, options)
