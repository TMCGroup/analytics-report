from django.core.management import BaseCommand

from reports.models import Voice


class Command(BaseCommand):
    def handle(self, *args, **options):
        Voice.get_data(project_name='SMS Maama')

        self.stdout.write(self.style.SUCCESS('Successfully added voice data'))
