from django.core.management import BaseCommand
from reports.models import Group, Workspace


class Command(BaseCommand):
    def handle(self, *args, **options):
            Workspace.get_rapidpro_workspaces()
            self.stdout.write(self.style.SUCCESS('Successfully added workspace data'))
