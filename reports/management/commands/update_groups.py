from django.core.management import BaseCommand
from reports.models import Group, RapidproKey


class Command(BaseCommand):
    def handle(self, *args, **options):
            RapidproKey.get_rapidpro_groups()
            self.stdout.write(self.style.SUCCESS('Successfully added groups'))
