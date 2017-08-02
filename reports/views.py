import os
import datetime as datetime
import StringIO
from django.conf import settings
from django.core.mail import EmailMessage
from analyticreports import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from .models import Contact, Message, Run, Flow, Group, Project, CampaignEvent, Campaign, Project, Voice, Email
from django.template.loader import render_to_string
from django.utils.timezone import now
from itertools import chain
from django.views.generic.base import View
import csv
import json
import datetime


def dashboard(request):
    projects = Project.get_all_projects()
    return render(request, 'report/dashboard.html', locals())


def project_groups_detail(request):  # (request, name) include project name to make it be the the one selected when the
    # based on clicked on project

    mega_poc = Project.objects.get(name='mCRAG')
    group = mega_poc.group.all()
    group_list = Project.get_project_data(name='mCRAG')
    project_list = Project.objects.filter(name='mCRAG').values_list('group__name', flat=True)
    contacts = Contact.get_project_contacts(project_list=project_list)
    c = Contact.objects.filter(uuid="3a8e1aee-15f5-41aa-9580-84bd68641e6d").values_list('groups')
    return render(request, 'report/project_group.html', locals())


def report_template_one(request, project_id):
    project = Project.objects.get(id=project_id)
    project_groups = project.group.all()
    project_groups_count = project.group.count()
    project_group_list = Project.get_project_data(name=project.name)
    voice_platiform = Voice.objects.filter(project=project).all()

    group_list = []

    for group in project_groups:
        group_list.append(group.name)

    contacts = Contact.get_project_contacts(project_list=group_list)

    weekly_contacts = Contact.get_weekly_project_contacts(project_list=group_list)

    weekly_contacts_value_list = Contact.get_all_project_contacts_value_list(project_list=group_list)
    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)

    weekly_sent_messages = Message.get_weekly_sent_messages(contact_urns_list)
    weekly_delivered_messages = Message.get_weekly_delivered_messages(contact_urns_list)
    weekly_failed_messages = Message.get_weekly_failed_messages(contact_urns_list)
    weekly_hanging_messages = Message.get_weekly_hanging_messages(contact_urns_list)
    weekly_unread_messages = Message.get_weekly_unread_messages(contact_urns_list)
    weekly_campaign_events = CampaignEvent.get_campaign_event()
    groups = Group.get_all_groups()

    return render(request, 'report/template_one.html', locals())


def report_template_one_pdf(request, project_id):
    project = Project.objects.get(id=project_id)
    project_groups = project.group.all()
    project_groups_count = project.group.count()
    project_group_list = Project.get_project_data(name=project.name)
    voice_platiform = Voice.objects.filter(project=project).all()

    group_list = []

    for group in project_groups:
        group_list.append(group.name)

    contacts = Contact.get_project_contacts(project_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_list=group_list)
    contact_counts = Contact.get_project_contacts_count(project_list=group_list)
    weekly_contacts_value_list = Contact.get_all_project_contacts_value_list(project_list=group_list)
    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)

    weekly_sent_messages = Message.get_weekly_sent_messages(contact_urns_list)
    weekly_delivered_messages = Message.get_weekly_delivered_messages(contact_urns_list)
    weekly_failed_messages = Message.get_weekly_failed_messages(contact_urns_list)
    weekly_hanging_messages = Message.get_weekly_hanging_messages(contact_urns_list)
    weekly_unread_messages = Message.get_weekly_unread_messages(contact_urns_list)
    weekly_campaign_events = CampaignEvent.get_campaign_event()
    groups = Group.get_all_groups()

    return render(request, 'report/my-pdf.html', locals())


def export_to_csv(request, project_id):
    project = Project.objects.get(id=project_id)
    voice_platiform = Voice.objects.filter(project=project).all()
    datetime_variable = datetime.datetime.now()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s_report_%s.csv"' % (project.name, datetime_variable)
    project_groups = project.group.all()
    group_list = []
    for group in project_groups:
        group_list.append(group.name)
    contacts = Contact.get_project_contacts(project_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_list=group_list)
    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)
    weekly_sent_messages = Message.get_weekly_sent_messages(contact_urns_list)
    weekly_delivered_messages = Message.get_weekly_delivered_messages(contact_urns_list)
    weekly_failed_messages = Message.get_weekly_failed_messages(contact_urns_list)
    weekly_hanging_messages = Message.get_weekly_hanging_messages(contact_urns_list)
    campaign_events = CampaignEvent.get_campaign_event()
    groups = Group.get_all_groups()

    writer = csv.writer(response)
    writer.writerow([])
    writer.writerow(['%s Report' % project.name])
    writer.writerow(['%s Groups' % project.name])
    writer.writerow(['Group', 'Number of participants'])
    for project_group in project_groups:
        writer.writerow([project_group.name, project_group.count])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['%s Contacts' % project.name])
    writer.writerow(['Contact Number', 'Contact Name', 'Group', 'Created on / Joined on'])
    for contact in contacts:
        writer.writerow([contact.urns, contact.name, contact.groups, contact.created_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['%s Weekly Joined Contacts' % project.name])
    writer.writerow(['Contact Number', 'Contact Name', 'Group', 'Created on / Joined on'])
    for contact in weekly_contacts:
        writer.writerow([contact.urns, contact.name, contact.groups, contact.created_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['%s Weekly Sent Messages' % project.name])
    writer.writerow(['Contact Number', 'Message', 'Status', 'Sent On'])
    for message in weekly_sent_messages:
        writer.writerow([message.urn, message.text, message.status, message.sent_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['%s Weekly Delivered Messages' % project.name])
    writer.writerow(['Contact Number', 'Message', 'Status', 'Sent On'])
    for message in weekly_delivered_messages:
        writer.writerow([message.urn, message.text, message.status, message.sent_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['%s Weekly Failed Messages' % project.name])
    writer.writerow(['Contact Number', 'Message', 'Status', 'Sent On'])
    for message in weekly_failed_messages:
        writer.writerow([message.urn, message.text, message.status, message.sent_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['%s Weekly Hanging Messages' % project.name])
    writer.writerow(['Contact Number', 'Message', 'Status', 'Sent On'])
    for message in weekly_hanging_messages:
        writer.writerow([message.urn, message.text, message.status, message.sent_on, ])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['Contact Number', 'Reason for call', 'Date'])
    for call in voice_platiform:
        writer.writerow([call.contact, call.reason, call.created_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow([])

    return response


def send_csv_attachment_email(request, project_id):
    csv_file = StringIO.StringIO()

    project = Project.objects.get(id=project_id)
    datetime_variable = datetime.date.today()
    project_groups = project.group.all()
    voice_platiform = Voice.objects.filter(project=project).all()
    group_list = []
    for group in project_groups:
        group_list.append(group.name)
    contacts = Contact.get_project_contacts(project_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_list=group_list)
    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)
    weekly_sent_messages = Message.get_weekly_sent_messages(contact_urns_list)
    weekly_delivered_messages = Message.get_weekly_delivered_messages(contact_urns_list)
    weekly_failed_messages = Message.get_weekly_failed_messages(contact_urns_list)
    weekly_hanging_messages = Message.get_weekly_hanging_messages(contact_urns_list)
    campaign_events = CampaignEvent.get_campaign_event()
    groups = Group.get_all_groups()

    writer = csv.writer(csv_file)
    writer.writerow([])
    writer.writerow(['%s Report' % project.name])
    writer.writerow(['Report Date: %s' % datetime_variable])
    writer.writerow(['Compiled / Reported by: %s' % request.user])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['All %s Groups' % project.name])
    writer.writerow(['Group', 'Number of participants'])
    for project_group in project_groups:
        writer.writerow([project_group.name, project_group.count])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['All %s Contacts' % project.name])
    writer.writerow(['Contact Number', 'Contact Name', 'Group(s)', 'Created on / Joined on'])
    for contact in contacts:
        writer.writerow([contact.urns, contact.name, contact.groups, contact.created_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['%s Weekly Enrolled Contacts' % project.name])
    writer.writerow(['Contact Number', 'Contact Name', 'Group(s)', 'Created on / Joined on'])
    for contact in weekly_contacts:
        writer.writerow([contact.urns, contact.name, contact.groups, contact.created_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['%s Weekly Delivered Messages' % project.name])
    writer.writerow(['Weekly Delivered Messages Count %s' % weekly_delivered_messages.count()])
    writer.writerow(['Contact Number', 'Message', 'Status', 'Sent On'])
    for message in weekly_delivered_messages:
        writer.writerow([message.urn, message.text.encode("utf8"), message.status, message.sent_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['%s Weekly Failed Messages' % project.name])
    writer.writerow(['Weekly Failed Messages Count %s' % weekly_failed_messages.count()])
    writer.writerow(['Contact Number', 'Message', 'Status', 'Sent On'])
    for message in weekly_failed_messages:
        writer.writerow([message.urn, message.text.encode("utf8"), message.status, message.sent_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['%s Weekly Hanging Messages' % project.name])
    writer.writerow(['Weekly Hanging Messages Count %s' % weekly_hanging_messages.count()])
    writer.writerow(['Contact Number', 'Message', 'Status', 'Sent On'])
    for message in weekly_hanging_messages:
        writer.writerow([message.urn, message.text.encode("utf8"), message.status, message.sent_on, ])
    writer.writerow([])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['Contact Number', 'Reason for call', 'Date'])
    for call in voice_platiform:
        writer.writerow([call.contact, call.reason, call.created_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow([])
    # writer.writerow([])
    # writer.writerow(['%s Weekly Sent Messages' % project.name])
    # writer.writerow(['Contact Number', 'Message', 'Status', 'Sent On'])
    # for message in weekly_sent_messages:
    #     writer.writerow([message.urn, message.text.encode("utf8"), message.status, message.sent_on])

    # Email.email_report(csv_file=csv_file.getvalue(), project_id=project.id)
    subject = '%s Weekly Report %s' % (project.name, datetime_variable)
    email = EmailMessage(
        subject,
        'Please find attached a sample of the csv file attachment, voice data and pdf view to be included '
        'during course of the week.',
        settings.EMAIL_HOST_USER,
        ['faithnassiwa@gmail.com'],
    )
    email.attach('%s_report_%s.csv' % (project.name, datetime_variable), csv_file.getvalue(), 'text/csv')
    email.send()
    return HttpResponse("Email Sent")


def getdatatest(request):
    data = Voice.get_data(proj="mCrag")
    lss = []
    for d in data:
        contact = d['phone_number']
        lss.append(contact)

    return HttpResponse("Voice data added")
    # return render(request, 'report/data.html', locals())


