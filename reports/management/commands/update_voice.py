from django.core.management import BaseCommand

from reports.models import Voice, ArtContact, CDR


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Voice.get_data(project_name='SMS Maama')
        # self.stdout.write(self.style.SUCCESS('Successfully added project voice data'))
        ArtContact.fetch_voice_art_contact_data()
        self.stdout.write(self.style.SUCCESS('Successfully updated art contacts data'))
        CDR.fetch_voice_cdr_data()
        self.stdout.write(self.style.SUCCESS('Successfully updated cdr data'))


