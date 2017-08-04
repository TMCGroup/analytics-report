from django.core.management import BaseCommand
from django.utils.timezone import now
from reports.models import Group, Contact, Message, Run


class Command(BaseCommand):
    def handle(self, *args, **options):
        updated = Message.assign_foreignkey()
        self.stdout.write(self.style.SUCCESS('Successfully added %d messages' % updated))
