# noinspection PyUnresolvedReferences
import datetime
import hashlib
import json
import operator
import numpy as np
import urllib2
from __builtin__ import reduce
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import models
from django.db.models import Q
from temba_client.v2 import TembaClient
import mysql.connector

tz = 'Africa/Kampala'
day = (datetime.datetime.now() - datetime.timedelta(1)).isoformat()
week = (datetime.datetime.now() - datetime.timedelta(7)).isoformat()
month = (datetime.datetime.now() - datetime.timedelta(90)).isoformat()
year = (datetime.datetime.now() - datetime.timedelta(365)).isoformat()

class Workspace(models.Model):
    name = models.CharField(max_length=200)
    host = models.CharField(max_length=200)
    key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['-created_at', ]

    @classmethod
    def get_rapidpro_workspaces(cls):
        workspaces = cls.objects.all()
        for workspace in workspaces:
            client = TembaClient(workspace.host, workspace.key)
            Group.add_groups(client=client)
            Contact.save_contacts(client=client, workspace=workspace)
            Flow.add_flows(client=client)
            Run.add_runs(client=client)
            Campaign.add_campaigns(client=client)
            CampaignEvent.add_campaign_events(client=client)

        return cls.objects.count()

    def __unicode__(self):
        return self.name


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
        return added

    @classmethod
    def group_exists(cls, group):
        return cls.objects.filter(uuid=group.uuid).exists()

    @classmethod
    def get_all_groups(cls):
        return cls.objects.all()

    def __unicode__(self):
        return self.name


class Flow(models.Model):
    uuid = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    expires = models.IntegerField(null=True)
    active_runs = models.IntegerField(null=True)
    complete_runs = models.IntegerField(null=True)
    interrupted_runs = models.IntegerField(null=True)
    expired_runs = models.IntegerField(null=True)
    created_on = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['name', ]

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


class Project(models.Model):
    name = models.CharField(max_length=200)
    group = models.ManyToManyField(Group, related_name='groups')
    flows = models.ManyToManyField(Flow, related_name='flows')
    lead = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['name', ]

    @classmethod
    def get_project(cls, name):
        return cls.objects.filter(name=name, active=True)

    @classmethod
    def get_project_voice_data(cls):
        projects = cls.objects.filter(active=True).all()
        for project in projects:
            Voice.get_data(project_name=project.name)
        return

    @classmethod
    def get_all_projects(cls):
        return cls.objects.filter(active=True).all()

    def __unicode__(self):
        return self.name


class Contact(models.Model):
    uuid = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True, blank=True)
    language = models.CharField(max_length=50, null=True, blank=True)
    urns = models.CharField(max_length=100, null=True, blank=True)
    groups = models.TextField(null=True, blank=True)
    fields = models.TextField(null=True, blank=True)
    blocked = models.BooleanField(default=False)
    stopped = models.BooleanField(default=False)
    created_on = models.DateTimeField(null=True)
    modified_on = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    workspace = models.ForeignKey(Workspace, blank=True, null=True)

    class Meta:
        ordering = ['-created_on', ]

    @classmethod
    def save_contacts(cls, client, workspace):
        added = 0
        for contact_batch in client.get_contacts(after=month).iterfetches(retry_on_rate_exceed=True):
            for contact in contact_batch:
                groups = []
                if contact.groups is not None:
                    for group in contact.groups:
                        groups.append(group.name)
                else:
                    pass

                if cls.contact_exists(contact):
                    cls.objects.filter(uuid=contact.uuid).update(name=contact.name,
                                                                 language=contact.language,
                                                                 urns=cls.clean_contacts(contact),
                                                                 groups=groups,
                                                                 fields=contact.fields,
                                                                 blocked=contact.blocked,
                                                                 stopped=contact.stopped,
                                                                 created_on=contact.created_on,
                                                                 modified_on=contact.modified_on, workspace=workspace)

                else:
                    cls.objects.create(uuid=contact.uuid, name=contact.name,
                                       language=contact.language,
                                       urns=cls.clean_contacts(contact), groups=groups,
                                       fields=contact.fields,
                                       blocked=contact.blocked, stopped=contact.stopped,
                                       created_on=contact.created_on,
                                       modified_on=contact.modified_on, workspace=workspace)

                    added += 1

                contact = Contact.objects.filter(uuid=contact.uuid).first()
                client = TembaClient(contact.workspace.host, contact.workspace.key)
                Message.save_messages(client, contact)

        return added

    @classmethod
    def contact_exists(cls, contact):
        return cls.objects.filter(uuid=contact.uuid).exists()

    @classmethod
    def urns_exists(cls, number):
        return cls.objects.filter(urns=number).exists()

    @classmethod
    def get_all_contacts(cls):
        return cls.objects.all().order_by('-created_on')

    @classmethod
    def get_project_contacts(cls, project_groups_list):
        if len(project_groups_list) > 0:
            query = reduce(operator.or_, (Q(groups__contains=item) for item in project_groups_list))
            return cls.objects.filter(query).all()
        else:
            return "No projects added yet"

    @classmethod
    def get_project_contacts_count(cls, project_groups_list):
        if len(project_groups_list) > 0:
            query = reduce(operator.or_, (Q(groups__contains=item) for item in project_groups_list))
            return cls.objects.filter(query).count()
        else:
            return "No projects added yet"

    @classmethod
    def get_weekly_project_contacts(cls, project_groups_list):
        if len(project_groups_list) > 0:
            query = reduce(operator.or_, (Q(groups__contains=item) for item in project_groups_list))
            date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
            return cls.objects.filter(query, created_on__range=(date_diff, datetime.datetime.now())).all()
        else:
            return "No projects added yet"

    @classmethod
    def get_all_project_contacts_value_list(cls, project_groups_list):
        if len(project_groups_list) > 0:
            query = reduce(operator.or_, (Q(groups__contains=item) for item in project_groups_list))
            return cls.objects.filter(query).values_list('urns')
        else:
            return "No projects added yet"

    @classmethod
    def get_contacts_count(cls):
        date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
        return cls.objects.filter(created_on__range=(date_diff, datetime.datetime.now())).count()

    @classmethod
    def get_project_contacts_percentage(cls, contact_variable, project_groups_list):
        if len(project_groups_list) > 0:
            project_contacts_total = cls.get_project_contacts_count(project_groups_list)
            if contact_variable > 0:
                return round(float(contact_variable) / float(project_contacts_total) * 100, 2)
            elif contact_variable == 0:
                return 0
            elif project_contacts_total == 0:
                return "Divide by zero error"
            else:
                pass
        else:
            return "No projects added yet"

    @classmethod
    def get_all_registered_contacts(cls, groups_list):
        if len(groups_list) > 0:
            query = reduce(operator.or_, (Q(groups__contains=item) for item in groups_list))
            return cls.objects.filter(query).all()

    @classmethod
    def get_all_unregistered_contacts(cls, groups_list):
        if len(groups_list) > 0:
            query = reduce(operator.or_, (Q(groups__contains=item) for item in groups_list))
            return cls.objects.exclude(query).all()

    @classmethod
    def get_all_contacts_percentage(cls, contact_variable, groups_list):
        if len(groups_list) > 0:
            all_contacts_total = cls.objects.count()
            if contact_variable > 0:
                return round(float(contact_variable) / float(all_contacts_total) * 100, 2)
            elif contact_variable == 0:
                return 0
            elif all_contacts_total == 0:
                return "Divide by zero error"
            else:
                pass
        else:
            return "No groups added yet"

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
    contact = models.ForeignKey(Contact, null=True, blank=True)
    urn = models.CharField(max_length=200, null=True, blank=True)
    channel = models.CharField(max_length=200, null=True, blank=True)
    direction = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=200, null=True, blank=True)
    visibility = models.CharField(max_length=200, null=True, blank=True)
    text = models.CharField(max_length=1000, null=True, blank=True)
    labels = models.CharField(max_length=200, null=True, blank=True)
    created_on = models.DateTimeField(null=True, blank=True)
    sent_on = models.DateTimeField(null=True, blank=True)
    modified_on = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['-created_on', ]

    @classmethod
    def save_messages(cls, client, contact):
        added = 0
        for message_batch in client.get_messages(contact=contact.uuid, after=month).iterfetches(
                retry_on_rate_exceed=True):  # to get all messages including failed filter by contact.uuid instead
            # of folder
            for message in message_batch:
                if not cls.message_exists(message):
                    if not Contact.objects.filter(uuid=message.contact.uuid).exists():
                        contact = Contact.objects.create(uuid=message.contact.uuid, name=message.contact.name,
                                                         urns=cls.clean_message_urn(message),
                                                         )
                        cls.objects.create(msg_id=message.id, broadcast=message.broadcast, contact=contact,
                                           urn=cls.clean_message_urn(message), channel=message.channel,
                                           direction=message.direction,
                                           type=message.type, status=message.status, visibility=message.visibility,
                                           text=message.text, labels=message.labels, created_on=message.created_on,
                                           sent_on=message.sent_on, modified_on=message.modified_on)
                        added += 1
                    else:
                        contact = Contact.objects.filter(uuid=message.contact.uuid).first()
                        cls.objects.create(msg_id=message.id, broadcast=message.broadcast, contact=contact,
                                           urn=cls.clean_message_urn(message), channel=message.channel,
                                           direction=message.direction,
                                           type=message.type, status=message.status, visibility=message.visibility,
                                           text=message.text, labels=message.labels, created_on=message.created_on,
                                           sent_on=message.sent_on, modified_on=message.modified_on)
                        added += 1
                else:  # cater for update in status mainly for hanging messages taking 48hours delivery receipt
                    Message.objects.filter(msg_id=message.id).update(broadcast=message.broadcast,
                                                                     channel=message.channel,
                                                                     direction=message.direction,
                                                                     type=message.type, status=message.status,
                                                                     visibility=message.visibility,
                                                                     modified_on=message.modified_on)

        return added

    @classmethod
    def message_exists(cls, message):
        return cls.objects.filter(msg_id=message.id).exists()

    @classmethod
    def get_all_outgoing_messages(cls):
        return cls.objects.filter(direction='out').exclude(status='queued').all()

    @classmethod
    def get_all_incoming_messages(cls):
        return cls.objects.filter(direction='in').all()

    @classmethod
    def get_all_specific_incoming_messages(cls, contacts_list):
        if len(contacts_list) > 0:
            query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
            return cls.objects.filter(query, direction='in').all()
        else:
            return "No contacts yet"

    @classmethod
    def get_all_project_incoming_messages(cls, contacts_list):
        if len(contacts_list) > 0:
            query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
            return cls.objects.filter(query, direction='in').all()
        else:
            return "No project contacts yet"

    @classmethod
    def get_all_project_outgoing_messages(cls, contacts_list):
        if len(contacts_list) > 0:
            query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
            return cls.objects.filter(query, direction='out').exclude(status='queued').all()
        else:
            return "No project contacts yet"

    @classmethod
    def get_weekly_sent_messages(cls, contacts_list):
        if len(contacts_list) > 0:
            query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
            date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
            return cls.objects.filter(query, direction='out', sent_on__range=(date_diff, datetime.datetime.now())) \
                .exclude(status='queued').all()
        else:
            return "No project contacts yet"

    @classmethod
    def get_weekly_delivered_messages(cls, contacts_list):
        if len(contacts_list) > 0:
            query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
            date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
            return cls.objects.filter(query, direction='out', status='delivered',
                                      sent_on__range=(date_diff, datetime.datetime.now())).all()
        else:
            return "No project contacts yet"

    @classmethod
    def get_weekly_failed_messages(cls, contacts_list):
        if len(contacts_list) > 0:
            query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
            date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
            return cls.objects.filter(query, status='failed', direction='out',
                                      sent_on__range=(date_diff, datetime.datetime.now())).all()
        else:
            return "No project contacts yet"

    @classmethod
    def get_weekly_hanging_messages(cls, contacts_list):
        if len(contacts_list) > 0:
            query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
            date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
            return cls.objects.filter(query, direction='out', sent_on__range=(date_diff, datetime.datetime.now())) \
                .exclude(status__in=['delivered', 'failed', 'handled', 'queued']).all()
        else:
            return "No project contacts yet"

    @classmethod
    def get_monthly_failed_messages(cls, contacts_list):
        if len(contacts_list) > 0:
            query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
            date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
            return cls.objects.filter(query, sent_on__range=(date_diff, datetime.datetime.now())).exclude(
                status='failed').all()
        else:
            return "No project contacts yet"

    @classmethod
    def get_cost_of_incoming_messages(cls, number_of_incoming_messages):
        return number_of_incoming_messages * 70

    @classmethod
    def get_cost_of_outgoing_messages(cls, number_of_outgoing_messages):
        return number_of_outgoing_messages * 25

    @classmethod
    def get_project_weekly_messages_percentage(cls, message_variable, contacts_list):
        if len(contacts_list) > 0:
            project_weekly_sent_messages_total = cls.get_weekly_sent_messages(contacts_list).count()
            if message_variable > 0:
                return str(round(float(message_variable) / float(project_weekly_sent_messages_total) * 100, 1)) + "%"
            elif message_variable == 0:
                return 0
            elif project_weekly_sent_messages_total == 0:
                return "Divide by zero error"
            else:
                pass
        else:
            return "No project contacts yet"

    @classmethod
    def get_all_project_messages(cls, contacts_list):
        query = reduce(operator.or_, (Q(urn__contains=contact) for contact in contacts_list))
        date_diff = datetime.datetime.now() - datetime.timedelta(days=42)
        return cls.objects.filter(query, sent_on__range=(date_diff, datetime.datetime.now())).all().order_by('urn')

    @classmethod
    def clean_message_urn(cls, message):
        if message.urn is not None and 'tel:' in message.urn:
            return message.urn[4:]
        else:
            return message.urn

    def __unicode__(self):
        return self.urn


class Campaign(models.Model):
    uuid = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    group = models.CharField(max_length=200, blank=True, null=True)
    created_on = models.DateTimeField()
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)

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
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['-created_on', ]

    @classmethod
    def add_campaign_events(cls, client):
        added = 0
        for campaign_events_batch in client.get_campaign_events().iterfetches(retry_on_rate_exceed=True):
            for campaign_event in campaign_events_batch:
                if not cls.campaign_event_exists(campaign_event):
                    cls.objects.create(uuid=campaign_event.uuid,
                                       campaign={'uuid': campaign_event.campaign.uuid,
                                                 'name': campaign_event.campaign.name},
                                       relative_to=campaign_event.relative_to, offset=campaign_event.offset,
                                       unit=campaign_event.unit, delivery_hour=campaign_event.delivery_hour,
                                       message=campaign_event.message, flow=campaign_event.flow,
                                       created_on=campaign_event.created_on)
                    added += 1
                else:
                    cls.objects.filter(uuid=campaign_event.uuid).update(
                        relative_to=campaign_event.relative_to, offset=campaign_event.offset,
                        unit=campaign_event.unit, delivery_hour=campaign_event.delivery_hour,
                        message=campaign_event.message, flow=campaign_event.flow,
                        created_on=campaign_event.created_on)
                    added += 1
        return added

    @classmethod
    def campaign_event_exists(cls, campaign_event):
        return cls.objects.filter(uuid=campaign_event.uuid).exists()

    @classmethod
    def get_campaign_event(cls):
        return cls.objects.all()

    def __unicode__(self):
        return self.uuid


class Run(models.Model):
    run_id = models.IntegerField()
    flow = models.ForeignKey(Flow, null=True, blank=True)
    contact = models.ForeignKey(Contact, null=True, blank=True)
    responded = models.BooleanField(default=False)
    exit_type = models.CharField(max_length=100, null=True, blank=True)
    values = models.TextField(blank=True, null=True)
    exited_on = models.DateTimeField(null=True)
    created_on = models.DateTimeField()
    modified_on = models.DateTimeField()
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['-created_on', ]

    @classmethod
    def add_runs(cls, client):
        added = 0
        for run_batch in client.get_runs(after=week).iterfetches(retry_on_rate_exceed=True):
            for run in run_batch:
                if not cls.run_exists(run):
                    if not (Contact.objects.filter(uuid=run.contact.uuid).exists() & Flow.objects.filter
                        (uuid=run.flow.uuid).exists()):
                        contact = Contact.objects.create(uuid=run.contact.uuid, name=run.contact.name)
                        flow = Flow.objects.create(uuid=run.flow.uuid, name=run.flow.name)
                        run_instance = cls.objects.create(run_id=run.id, flow=flow, contact=contact,
                                                          responded=run.responded, values=run.values,
                                                          exit_type=run.exit_type, exited_on=run.exited_on,
                                                          created_on=run.created_on, modified_on=run.modified_on)
                        added += 1
                        Value.add_values(run=run_instance, values=run.values)
                    else:
                        contact = Contact.objects.filter(uuid=run.contact.uuid).first()
                        flow = Flow.objects.filter(uuid=run.flow.uuid).first()
                        run_instance = cls.objects.create(run_id=run.id, flow=flow, contact=contact,
                                                          responded=run.responded, values=run.values,
                                                          exit_type=run.exit_type, exited_on=run.exited_on,
                                                          created_on=run.created_on, modified_on=run.modified_on)
                        added += 1
                        Value.add_values(run=run_instance, values=run.values)

        return added

    @classmethod
    def run_exists(cls, run):
        return cls.objects.filter(run_id=run.id).exists()

    def __unicode__(self):
        return self.run_id


class Value(models.Model):
    value_name = models.CharField(max_length=100, blank=True, null=True)
    value = models.CharField(max_length=1000, blank=True, null=True)
    category = models.CharField(max_length=1000, blank=True, null=True)
    node = models.CharField(max_length=1000, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['-time', ]

    @classmethod
    def add_values(cls, run, values):
        added = 0
        for outer_key, inner_dictionary in values.items():
            if not cls.value_exists(run=run):
                cls.objects.create(value_name=outer_key, value=values[outer_key].value,
                                   category=values[outer_key].category,
                                   node=values[outer_key].node,
                                   time=values[outer_key].time, run=run)
                added += 1
            else:
                cls.objects.filter(run=run).update(value_name=outer_key, value=values[outer_key].value,
                                                   category=values[outer_key].category,
                                                   node=values[outer_key].node,
                                                   time=values[outer_key].time)

        return added

    @classmethod
    def value_exists(cls, run):
        return cls.objects.filter(run=run).exists()

    def __unicode__(self):
        return self.value


class Email(models.Model):
    name = models.CharField(max_length=100)
    email_address = models.EmailField(max_length=200)
    project = models.ManyToManyField(Project)

    class Meta:
        ordering = ['name', ]

    @classmethod
    def add_email(cls, name, email_address, project):
        return cls.objects.create(name=name, email_address=email_address, project=project)

    @classmethod
    def get_project_mailing_list(cls, project_id):
        project = Project.objects.get(id=project_id)
        mailing_list = []
        project_report_recipients = cls.objects.filter(project__name=project.name).all()
        for project_report_recipient in project_report_recipients:
            mailing_list.append(project_report_recipient.email_address)

        return mailing_list

    @classmethod
    def get_report_emails(cls, project_id):
        project = Project.objects.get(id=project_id)
        mailing_list = cls.get_project_mailing_list(project.id)
        report_datetime = datetime.datetime.now()
        email_subject = '%s Weekly ( %s ) Report' % (project.name, report_datetime)
        email_body = render_to_string('report/report_email_body.html')
        email_message = EmailMultiAlternatives(email_subject, email_body, settings.EMAIL_HOST_USER, mailing_list)
        email_message.attach_alternative(email_body, "text/html")
        return email_message

    def __unicode__(self):
        return self.name


class Voice(models.Model):
    id = models.IntegerField(primary_key=True)
    uuid = models.CharField(max_length=50)
    project = models.ForeignKey(Project)
    contact = models.ForeignKey(Contact)
    reason = models.TextField()
    advice = models.TextField()
    created_by = models.CharField(max_length=100)
    created_on = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-created_on', ]

    @classmethod
    def get_data(cls, project_name):
        url = "http://voice.tmcg.co.ug/~nicholas/data.php?project={0}".format(urllib2.quote(project_name))
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        data_set = json.load(response)
        for data in data_set:
            if cls.voice_id_exists(id=data['id']):
                pass
            else:
                urns = cls.clean_contact(data['phone'])
                if Contact.urns_exists(number=urns):
                    uuid = hashlib.md5(data['created_at']).hexdigest()
                    contact = Contact.objects.filter(urns=urns).first()
                    project = Project.objects.get(name=project_name)
                    cls.objects.create(id=data['id'], uuid=uuid, project=project, contact=contact,
                                       reason=data['reason_for_call'],
                                       advice=data['advice_given'], created_by=data['created_by'],
                                       created_on=data['created_at'])
                else:
                    pass

        return data_set

    @classmethod
    def voice_id_exists(cls, id):
        return cls.objects.filter(id=id).exists()

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

    @classmethod
    def get_weekly_voice_interaction(cls, project):
        date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
        return cls.objects.filter(created_on__range=(date_diff, datetime.datetime.now()), project=project).all()

    def __unicode__(self):
        return str(self.project)


class ArtContact(models.Model):
    voice_id = models.BigIntegerField()
    name = models.CharField(max_length=225, null=True)
    language_preference = models.BigIntegerField(null=True)
    gender = models.CharField(max_length=20)
    age = models.DateField(null=True)
    district = models.BigIntegerField(null=True)
    area = models.CharField(max_length=225, null=True)
    designation = models.CharField(max_length=225, null=True)
    sector = models.BigIntegerField(null=True)
    telephone_number = models.BigIntegerField()
    alt_number = models.CharField(max_length=225, null=True)
    date_of_consent = models.DateField(null=True)
    art_type = models.CharField(max_length=50, null=True)
    more_info = models.CharField(max_length=225, null=True)
    status = models.BigIntegerField(null=True)
    created_at = models.DateTimeField()
    created_by = models.BigIntegerField()

    @classmethod
    def fetch_voice_art_contact_data(cls):
        try:
            voice_server_connection = mysql.connector.connect(host=settings.VOICE_DB_HOST,
                                                              database=settings.VOICE_DB_NAME,
                                                              user=settings.VOICE_DB_USERNAME,
                                                              password=settings.VOICE_DB_PASSWORD)
            voice_cur = voice_server_connection.cursor()
            voice_cur.execute("SELECT * from art")
            voice_results = voice_cur.fetchall()

            for item in voice_results:
                if not cls.art_contact_exists(item[0]):
                    cls.objects.create(voice_id=item[0], name=item[1], language_preference=item[2], gender=item[3],
                                       age=item[4], district=item[5], area=item[6], designation=item[7], sector=item[8],
                                       telephone_number=item[9], alt_number=item[10], date_of_consent=item[11],
                                       art_type=item[12], more_info=item[13], status=item[14], created_at=item[15],
                                       created_by=item[16])
            voice_server_connection.close()
        except mysql.connector.Error as err:
            print("Unable to connect to Voice DB. Something went wrong: {}".format(err))


    @classmethod
    def art_contact_exists(cls, voice_id):
        return cls.objects.filter(voice_id=voice_id).exists()


class CDR(models.Model):
    acctid = models.BigIntegerField()
    calldate = models.DateTimeField(null=True)
    clid = models.CharField(max_length=80, null=True)
    src = models.CharField(max_length=80, null=True)
    dst = models.CharField(max_length=80, null=True)
    dcontext = models.CharField(max_length=80, null=True)
    channel = models.CharField(max_length=80, null=True)
    dstchannel = models.CharField(max_length=80, null=True)
    lastapp = models.CharField(max_length=80, null=True)
    lastdata = models.CharField(max_length=80, null=True)
    duration = models.IntegerField(null=True)
    billsec = models.IntegerField(null=True)
    enterq = models.DateTimeField(null=True)
    leaveq = models.DateTimeField(null=True)
    endcall = models.DateTimeField(null=True)
    disposition = models.CharField(max_length=45, null=True)
    amaflags = models.IntegerField(null=True)
    accountcode = models.CharField(max_length=20, null=True)
    userfield = models.CharField(max_length=225, null=True)
    uniqueid = models.CharField(max_length=32, null=True)
    linkedid = models.CharField(max_length=32, null=True)
    sequence = models.CharField(max_length=32, null=True)
    peeraccount = models.CharField(max_length=32, null=True)
    import_cdr = models.IntegerField(null=True)


    @classmethod
    def fetch_voice_cdr_data(cls):
        try:
            voice_server_connection = mysql.connector.connect(host=settings.VOICE_DB_HOST,
                                                              database=settings.VOICE_DB_NAME,
                                                              user=settings.VOICE_DB_USERNAME,
                                                              password=settings.VOICE_DB_PASSWORD)
            voice_cur = voice_server_connection.cursor()
            voice_cur.execute("SELECT * from cdr")
            voice_results = voice_cur.fetchall()

            for item in voice_results:
                if not cls.cdr_exists(item[0]):
                    cls.objects.create(acctid=item[0], calldate=item[1], clid=item[2], src=item[3],dst=item[4],
                                       dcontext=item[5], channel=item[6], dstchannel=item[7], lastapp=item[8],
                                       lastdata=item[9], duration=item[10], billsec=item[11],
                                       enterq=item[12], leaveq=item[13], endcall=item[14], disposition=item[15],
                                       amaflags=item[16], accountcode=item[17], userfield=item[18], uniqueid=item[19],
                                       linkedid=item[20], sequence=item[21], peeraccount=item[22], import_cdr=item[23])
            voice_server_connection.close()
        except mysql.connector.Error as err:
            print("Unable to connect to Voice DB. Something went wrong: {}".format(err))


    @classmethod
    def cdr_exists(cls, acctid):
        return cls.objects.filter(acctid=acctid).exists()
