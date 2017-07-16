from django.core.management import BaseCommand
from reports.models import Run, Contact, Flow
from temba_client.v2 import TembaClient

class Command(BaseCommand):
    def handle(self, *args, **options):
        client = TembaClient('hiwa.tmcg.co.ug', '3aac2aba67a0cf83dc0ea49151a05088277eb4d6')
        flows = Flow.add_flows(client=client)

        self.stdout.write(self.style.SUCCESS('Successfully added %d flows' % flows))
