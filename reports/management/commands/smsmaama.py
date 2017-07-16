from django.core.management import BaseCommand
from django.utils.timezone import now
from reports.models import Group, Contact, Message, Run


class Command(BaseCommand):
    def handle(self, *args, **options):
        Contact.clean_contacts()
        Message.clean_msg_contacts()
        #html_to_pdf_view()
        #this_day = now()
        #target = 'media/'+str(this_day)[:-22]+'.pdf'
        #Email.send_message_email(target)
        self.stdout.write(self.style.SUCCESS('Successfully cleaned'))
