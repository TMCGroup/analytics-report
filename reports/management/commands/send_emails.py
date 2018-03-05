from django.core.management import BaseCommand
from reports.views import email_report
from reports.models import Project


class Command(BaseCommand):
    def handle(self, *args, **options):
        projects = Project.objects.all()
        for project in projects:
            email_report(project_id=project.id)
            self.stdout.write(self.style.SUCCESS('Successfully added workspace data'))
