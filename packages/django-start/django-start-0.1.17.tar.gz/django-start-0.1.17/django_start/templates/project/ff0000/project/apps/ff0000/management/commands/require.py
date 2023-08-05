# Run python manage.py require to load the requirements in a given environment

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import logging
from os import system, environ        

class Command(BaseCommand):
    help = "Install the python requirements for a given environment."
    can_import_settings = False
    requires_model_validation = False
    def handle(self, *args, **options):
        """
        Install the python requirements for a given environment.
        """
        # assume project.settings.ENVIRONMENT else default to 'development'
        env = environ['DJANGO_SETTINGS_MODULE'].split(".")[-1]
        env = 'development' if env == 'settings' else env
        
        # Loop through available PyPi mirrors
        # See http://jacobian.org/writing/when-pypi-goes-down/
        installed = False
        mirrors = ['b.pypi', 'c.pypi', 'd.pypi', 'pypi',]
        while not installed and len(mirrors) > 0:
            mirror = mirrors.pop()
            result = system('pip install -i http://%s.python.org/simple -r ../deploy/requirements/base.txt -r ../deploy/requirements/%s.txt' % (mirror, env))
            installed = (result == 0)
        if installed:
            logging.info("Require success")
        else:
            logging.error("Could not install all requirements")