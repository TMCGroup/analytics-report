from django.core.management import BaseCommand
from reports.models import RapidproKey, Contact, Message
from temba_client.v2 import TembaClient


class Command(BaseCommand):
    def handle(self, *args, **options):
        added = 0
        keys = RapidproKey.get_workspaces()
        contacts = Contact.get_all_contacts()
        # for key in keys:
        #     client = TembaClient(key.host, key.key)
        client = TembaClient('hiwa.tmcg.co.ug', '3aac2aba67a0cf83dc0ea49151a05088277eb4d6')
        for contact in contacts:
            added = Message.save_messages(client=client, contact=contact)

        self.stdout.write(self.style.SUCCESS('Successfully added %d messages' % added))
