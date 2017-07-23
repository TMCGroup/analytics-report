from __builtin__ import reduce
import urllib2
import hashlib
import urllib
import json
from django.db import models
from django.conf import settings
from temba_client.v2 import TembaClient
from django.core.mail import EmailMessage
import datetime
from django.utils import timezone
import pytz
from django.urls import reverse
import operator
from django.db.models import Q

tz = 'Africa/Kampala'


class RapidproKey(models.Model):
    workspace = models.CharField(max_length=200)
    host = models.CharField(max_length=200)
    key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    @classmethod
    def get_rapidpro_groups(cls):
        keys = cls.objects.all()
        for rkey in keys:
            client = TembaClient(rkey.host, rkey.key)
            Group.add_groups(client=client)
            Contact.save_contacts(client=client)
            Flow.add_flows(client=client)
            Campaign.add_campaigns(client=client)
            CampaignEvent.add_campaign_events(client=client)

    @classmethod
    def get_workspaces(cls):
        return cls.objects.all()

    def __unicode__(self):
        return str(self.workspace)


class Group(models.Model):
    uuid = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    count = models.IntegerField()
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['name', ]

    @classmethod
    def add_groups(cls, client):
        added = 0
        for group_batch in client.get_groups().iterfetches(retry_on_rate_exceed=True):
            for group in group_batch:
                if cls.group_exists(group):
                    cls.objects.filter(uuid=group.uuid).update(name=group.name, count=group.count)
                    added += 0

                else:
                    cls.objects.create(uuid=group.uuid, name=group.name, count=group.count)
                    added += 1
                    # Flow.add_flows()  # remember to put in celery
        return added

    @classmethod
    def group_exists(cls, group):
        return cls.objects.filter(uuid=group.uuid).exists()

    @classmethod
    def get_all_groups(cls):
        return cls.objects.all()

    def __unicode__(self):
        return str(self.name)


class Project(models.Model):
    name = models.CharField(max_length=200)
    group = models.ManyToManyField(Group, related_name='groups')
    lead = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True, auto_now_add=False)

    @classmethod
    def get_project_data(cls, name):
        return cls.objects.filter(name=name, active=True).all()

    @classmethod
    def get_all_projects(cls):
        return cls.objects.filter(active=True).all()

    def __unicode__(self):
        return str(self.name)


class Contact(models.Model):
    uuid = models.CharField(max_length=200)
    name = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=255, null=True)
    urns = models.CharField(max_length=200)
    groups = models.TextField()
    fields = models.TextField(null=True, blank=True)
    blocked = models.BooleanField(default=False)
    stopped = models.BooleanField(default=False)
    created_on = models.DateTimeField(null=True)
    modified_on = models.DateTimeField(null=True)

    @classmethod
    def save_contacts(cls, client):
        added = 0
        for contact_batch in client.get_contacts().iterfetches(retry_on_rate_exceed=True):
            for contact in contact_batch:

                grp = []
                for g in contact.groups:
                    grp.append(g.name)
                if cls.contact_exists(contact):
                    con = cls.objects.get(uuid=contact.uuid)
                    for gp in con.groups:
                        if gp in grp:
                            grp.remove(gp)
                        else:
                            grp.append(gp)

                    ct = cls.objects.filter(uuid=contact.uuid).update(name=contact.name, language=contact.language,
                                                                      urns=cls.clean_contacts(contact), groups=grp,
                                                                      fields=contact.fields,
                                                                      blocked=contact.blocked, stopped=contact.stopped,
                                                                      created_on=contact.created_on,
                                                                      modified_on=contact.modified_on)
                    Message.save_messages(client, contact=ct)
                    Run.add_runs(client, contact=con)

                    grp[:] = []

                else:

                    ct = cls.objects.create(uuid=contact.uuid, name=contact.name, language=contact.language,
                                            urns=cls.clean_contacts(contact), groups=grp, fields=contact.fields,
                                            blocked=contact.blocked, stopped=contact.stopped,
                                            created_on=contact.created_on, modified_on=contact.modified_on)
                    Message.save_messages(client, contact=ct)
                    Run.add_runs(client, contact=ct)
                    grp[:] = []

                    added += 1

        return added

    @classmethod
    def contact_exists(cls, contact):
        return cls.objects.filter(uuid=contact.uuid).exists()
      
    @classmethod
    def urns_exists(cls, number):
        return cls.objects.filter(urns=number).exists()

    @classmethod
    def get_all_contacts(cls):
        return cls.objects.all()

    @classmethod
    def get_project_contacts(cls, project_list):
        query = reduce(operator.or_, (Q(groups__contains=item) for item in project_list))
        return cls.objects.filter(query).all()

    @classmethod
    def get_project_contacts_count(cls, project_list):
        query = reduce(operator.or_, (Q(groups__contains=item) for item in project_list))
        return cls.objects.filter(query).count()

    @classmethod
    def get_weekly_project_contacts(cls, project_list):
        query = reduce(operator.or_, (Q(groups__contains=item) for item in project_list))
        date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
        return cls.objects.filter(query, created_on__range=(date_diff, datetime.datetime.now())).all()

    @classmethod
    def get_all_project_contacts_value_list(cls, project_list):
        query = reduce(operator.or_, (Q(groups__contains=item) for item in project_list))
        return cls.objects.filter(query).values_list('urns')

    @classmethod
    def get_contacts_count(cls):
        date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
        return cls.objects.filter(created_on__range=(date_diff, datetime.datetime.now())).count()

    @classmethod
    def clean_contacts(cls, contact):
        for c in contact.urns:
            if 'tel:' in c:
                return c[4:]
            else:
                return contact.urns

    def __unicode__(self):
        return str(self.urns)


class Message(models.Model):
    msg_id = models.IntegerField()
    broadcast = models.IntegerField(null=True)
    contact = models.ForeignKey(Contact)
    urn = models.CharField(max_length=200)
    channel = models.CharField(max_length=200)
    direction = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    visibility = models.CharField(max_length=200)
    text = models.CharField(max_length=1000)
    labels = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    sent_on = models.DateTimeField(null=True, blank=True)
    modified_on = models.DateTimeField(null=True, blank=True)

    @classmethod
    def save_messages(cls, client, contact):
        added = 0

        for message_batch in client.get_messages(contact=contact).iterfetches(retry_on_rate_exceed=True):
            for message in message_batch:
                if not cls.message_exists(message):
                    cls.objects.create(msg_id=message.id, broadcast=message.broadcast, contact=contact,
                                       urn=cls.clean_msg_contacts(message), channel=message.channel,
                                       direction=message.direction,
                                       type=message.type, status=message.status, visibility=message.visibility,
                                       text=message.text, labels=message.labels, created_on=message.created_on,
                                       sent_on=message.sent_on, modified_on=message.modified_on)
                    added += 1

                    #  No need to update messages, they do not have any field that will be modified.
                else:
                    pass

        return added

    @classmethod
    def message_exists(cls, message):
        return cls.objects.filter(msg_id=message.id).exists()

    @classmethod
    def get_weekly_sent_messages(cls, contacts_list):
        query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
        date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
        return cls.objects.filter(query, direction='out', sent_on__range=(date_diff, datetime.datetime.now())).all()

    @classmethod
    def get_weekly_delivered_messages(cls, contacts_list):
        query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
        date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
        return cls.objects.filter(query, direction='out', status='delivered',
                                  sent_on__range=(date_diff, datetime.datetime.now())).all()

    @classmethod
    def get_weekly_failed_messages(cls, contacts_list):
        query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
        date_diff = datetime.datetime.now() - datetime.timedelta(days=21)  ## this is for testing
        return cls.objects.filter(query, status='failed', direction='out',
                                  sent_on__range=(date_diff, datetime.datetime.now())).all()

    @classmethod
    def get_weekly_hanging_messages(cls, contacts_list):
        query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
        date_diff = datetime.datetime.now() - datetime.timedelta(days=21)  ## this is for testing
        return cls.objects.filter(query, direction='out', sent_on__range=(date_diff, datetime.datetime.now())) \
            .exclude(status__in=["sent", "delivered", "handled", "errored", "failed", "resent"]).all()

    @classmethod
    def get_monthly_failed_messages(cls, contacts_list):
        query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
        date_diff = datetime.datetime.now() - datetime.timedelta(days=30)
        return cls.objects.filter(query, sent_on__range=(date_diff, datetime.datetime.now())).exclude(
            status='delivered').all()

    @classmethod
    def get_weekly_unread_messages(cls, contacts_list):
        query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
        date_diff = datetime.datetime.now() - datetime.timedelta(days=21)
        return cls.objects.filter(query, direction='out', status='errored',
                                  sent_on__range=(date_diff, datetime.datetime.now())).all()

    @classmethod
    def get_weekly_failed_messages_daily(cls, contact_list):
        # query = reduce(operator.or_, (Q(contact__groups__contains=item) for item in project_list))
        # query_2 = reduce(operator.or_, (Q(contact__in=item) for item in contact_qs))
        query_3 = reduce(operator.or_, (Q(urn__contains=item) for item in contact_list))
        date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
        return cls.objects.filter(direction='out', status='failed',
                                  sent_on__range=(date_diff, datetime.datetime.now())).all() \
 \
    # @classmethod
    # def get_weekly_failed_messages_daily(cls, contact_list):
    #     # query = reduce(operator.or_, (Q(contact__groups__contains=item) for item in project_list))
    #     # query_2 = reduce(operator.or_, (Q(contact__in=item) for item in contact_qs))
    #     query_3 = reduce(operator.or_, (Q(urn__contains=item) for item in contact_list))
    #     date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
    #     return cls.objects.filter(direction='out', status='delivered',
    #                               sent_on__range=(date_diff, datetime.datetime.now())).all()

    @classmethod
    def clean_msg_contacts(cls, msg):
        if 'tel:' in msg.urn:
            return msg.urn[4:]
        else:
            return msg.urn

    def __unicode__(self):
        return self.urn


class Flow(models.Model):
    uuid = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    expires = models.IntegerField()
    active_runs = models.IntegerField(null=True)
    complete_runs = models.IntegerField(null=True)
    interrupted_runs = models.IntegerField(null=True)
    expired_runs = models.IntegerField(null=True)
    created_on = models.DateTimeField()

    @classmethod
    def add_flows(cls, client):
        flows = client.get_flows().all()
        added = 0
        for flow in flows:
            if cls.flow_exists(flow):
                cls.objects.filter(uuid=flow.uuid).update(name=flow.name, expires=flow.expires,
                                                          active_runs=flow.runs.active,
                                                          complete_runs=flow.runs.completed,
                                                          interrupted_runs=flow.runs.interrupted,
                                                          expired_runs=flow.runs.expired, created_on=flow.created_on)
                added += 0
            else:
                cls.objects.create(uuid=flow.uuid, name=flow.name, expires=flow.expires,
                                   active_runs=flow.runs.active, complete_runs=flow.runs.completed,
                                   interrupted_runs=flow.runs.interrupted, expired_runs=flow.runs.expired,
                                   created_on=flow.created_on)
                added += 1

        return added

    @classmethod
    def flow_exists(cls, flow):
        return cls.objects.filter(uuid=flow.uuid).exists()

    def __unicode__(self):
        return self.name


class Campaign(models.Model):
    uuid = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    group = models.CharField(max_length=200, blank=True, null=True)
    created_on = models.DateTimeField()

    @classmethod
    def add_campaigns(cls, client):
        added = 0
        for campaign_batch in client.get_campaigns().iterfetches(retry_on_rate_exceed=True):
            for campaign in campaign_batch:
                if not cls.campaign_exists(campaign):
                    cls.objects.create(uuid=campaign.uuid, name=campaign.name,
                                       group=campaign.group, created_on=campaign.created_on)

                    added += 1
                else:
                    cls.objects.filter(uuid=campaign.uuid).update(name=campaign.name,
                                                                  group=campaign.group,
                                                                  created_on=campaign.created_on)
        return added

    @classmethod
    def campaign_exists(cls, campaign):
        return cls.objects.filter(uuid=campaign.uuid).exists()

    def __unicode__(self):
        return self.name


class CampaignEvent(models.Model):
    uuid = models.CharField(max_length=36)
    campaign = models.CharField(max_length=200)
    relative_to = models.CharField(max_length=100)
    offset = models.IntegerField()
    unit = models.CharField(max_length=7)
    delivery_hour = models.IntegerField()
    message = models.TextField(blank=True, null=True)
    flow = models.CharField(max_length=200, blank=True, null=True)
    created_on = models.DateTimeField()

    @classmethod
    def add_campaign_events(cls, client):
        added = 0
        for campaign_events_batch in client.get_campaign_events().iterfetches(retry_on_rate_exceed=True):
            for campaign_event in campaign_events_batch:
                if not cls.campaign_event_exists(campaign_event):
                    cls.objects.create(uuid=campaign_event.uuid,
                                       # campaign=campaign_event.campaign.uuid,
                                       campaign={'uuid': campaign_event.campaign.uuid,
                                                 'name': campaign_event.campaign.name},
                                       relative_to=campaign_event.relative_to, offset=campaign_event.offset,
                                       unit=campaign_event.unit, delivery_hour=campaign_event.delivery_hour,
                                       message=campaign_event.message, flow=campaign_event.flow,
                                       created_on=campaign_event.created_on)
                    added += 1
                else:
                    cls.objects.filter(uuid=campaign_event.uuid, campaign_event_id=campaign_event.id).update(
                        relative_to=campaign_event.relative_to, offset=campaign_event.offset,
                        unit=campaign_event.unit, delivery_hour=campaign_event.delivery_hour,
                        message=campaign_event.message, flow={'uuid': campaign_event.flow.uuid,
                                                              'name': campaign_event.flow.name},
                        created_on=campaign_event.created_on)
                    added += 1
        return added

    @classmethod
    def campaign_event_exists(cls, campaign_event):
        return cls.objects.filter(uuid=campaign_event.uuid).exists()

    # @classmethod testing out
    # def get_campaign_event(cls, message):
    #     return cls.objects.filter(message__iexact=message.text).all()

    @classmethod
    def get_campaign_event(cls):
        date_diff = datetime.datetime.now() - datetime.timedelta(days=21)
        return cls.objects.filter(created_on__range=(date_diff, datetime.datetime.now())).all()

    def __str__(self):
        return self.uuid


class Run(models.Model):
    run_id = models.IntegerField()
    flow = models.CharField(max_length=200)
    contact = models.ForeignKey(Contact)
    responded = models.BooleanField(default=False)
    exit_type = models.CharField(max_length=100, null=True, blank=True)
    exited_on = models.DateTimeField(null=True)
    created_on = models.DateTimeField()
    modified_on = models.DateTimeField()

    @classmethod
    def add_runs(cls, client, contact):
        added = 0
        for run_batch in client.get_runs(contact=contact).iterfetches(retry_on_rate_exceed=True):
            for run in run_batch:
                if not cls.run_exists(run):
                    r = cls.objects.create(run_id=run.id, flow=run.flow, contact=contact, responded=run.responded,
                                           exit_type=run.exit_type, exited_on=run.exited_on,
                                           created_on=run.created_on, modified_on=run.modified_on)
                    added += 1

        return added

    @classmethod
    def run_exists(cls, run):
        return cls.objects.filter(run_id=run.id).exists()

    def __unicode__(self):
        return str(self.run_id)

      
class Value(models.Model):
    value = models.CharField(max_length=100, blank=True)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)

    @classmethod
    def add_values(cls, run, values):
        added = 0
        for val in values:
            if not cls.value_exists(run=run):
                cls.objects.create(value=val, run=run)
                added += 1
        return added

    @classmethod
    def value_exists(cls, run):
        return cls.objects.filter(run=run).exists()

    def __str__(self):
        return str(self.value)


class Email(models.Model):
    name = models.CharField(max_length=100)
    email_address = models.EmailField(max_length=200)
    project = models.ForeignKey(Project)

    @classmethod
    def email_report(cls, pdf_file, csv_file, project_id):
        mailing_list = []
        email_addresses = cls.objects.filter(project__id=project_id).all()
        for email_address in email_addresses:
            mailing_list.append(email_address.email_address)

        email_body = '<h4>Please find attached the weekly report.</h4>'
        email_message = EmailMessage('mCRAG weekly report', email_body, settings.EMAIL_HOST_USER, mailing_list)
        email_message.attach_file(pdf_file)
        email_message.attach_file(csv_file)
        email_message.content_subtype = "html"
        return email_message.send()

    def __str__(self):
        return str(self.name)
      

class Voice(models.Model):
    id = models.IntegerField(primary_key=True)
    uuid = models.CharField(max_length=50)
    project = models.ForeignKey(Project)
    contact = models.ForeignKey(Contact)
    reason = models.TextField()
    advice = models.TextField()
    created_by = models.CharField(max_length=100)
    created_on = models.DateTimeField(null=True)

    @classmethod
    def get_data(cls, proj):
        url = "http://voice.tmcg.co.ug/~nicholas/data.php?project={0}".format(urllib2.quote(proj))
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        datas = json.load(response)
        for data in datas:
            if cls.voice_id_exists(id=data['id']):
                pass
            else:
                urns = cls.clean_contact(data['phone_number'])
                if Contact.urns_exists(number=urns):
                    uuid = hashlib.md5(data['created_at']).hexdigest()
                    obj = Contact.objects.filter(urns=urns).first()
                    pro = Project.objects.get(name=proj)
                    cls.objects.create(id=data['id'], uuid=uuid, project=pro, contact=obj,
                                       reason=data['reason_for_call'],
                                       advice=data['advice_given'], created_by=data['created_by'],
                                       created_on=data['created_at'])
                else:
                    pass

        return datas

    @classmethod
    def voice_id_exists(cls, id):
        return cls.objects.filter(uuid=id).exists()

    @classmethod
    def clean_contact(cls, contact):
        c = ''
        if len(contact) == 10:
            c = '+256' + contact[1:]
        elif len(contact) == 12:
            c = '+' + contact
        elif len(contact) == 9:
            c = '+256' + contact
        else:
            pass
        return c

    def __unicode__(self):
        return str(self.project)
