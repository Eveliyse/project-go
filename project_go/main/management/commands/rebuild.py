import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Drop the database and recreate the site'

    def handle(self, *args, **options):
        call_command('sqlflush')
        call_command('makemigrations')
        call_command('migrate')
        
        call_command('loaddata', os.path.join(settings.PROJECT_PATH, 'main/fixtures/auth_views_testdata.json'))
        call_command('loaddata', os.path.join(settings.PROJECT_PATH, 'main/fixtures/users_views_testdata.json'))
        call_command('loaddata', os.path.join(settings.PROJECT_PATH, 'main/fixtures/projects_views_testdata.json'))
