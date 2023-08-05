#!.env/bin/python
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.management import call_command

def main():
    call_command('flush', interactive=False)

if __name__ == '__main__':
    main()
