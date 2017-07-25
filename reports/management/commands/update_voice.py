from django.core.management import BaseCommand
from reports.models import Voice
from temba_client.v2 import TembaClient

class Command(BaseCommand):
    def handle(self, *args, **options):
        Voice.get_data(proj='SMS Maama')

        self.stdout.write(self.style.SUCCESS('Successfully added voice data'))
