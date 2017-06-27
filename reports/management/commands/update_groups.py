from django.core.management import BaseCommand
from reports.models import Group, RapidproKey


class Command(BaseCommand):
    def handle(self, *args, **options):
            RapidproKey.get_rapidpro_data()
            self.stdout.write(self.style.SUCCESS('Successfully added groups and contacts'))
