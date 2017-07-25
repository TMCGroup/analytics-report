import os
import datetime as datetime
from analyticreports import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from .models import Contact, Message, Run, Flow, Group, Project, CampaignEvent, Campaign, Project, Voice
from django.template.loader import render_to_string
from django.utils.timezone import now
from itertools import chain
from django.views.generic.base import View
import csv
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
    for project in project_groups:
        group_list.append(project.name)

    contacts = Contact.get_project_contacts(project_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_list=group_list)
    contact_counts = Contact.get_project_contacts_count(project_list=group_list)
    weekly_contacts_value_list = Contact.get_all_project_contacts_value_list(project_list=group_list)
    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)

    weekly_failed_messages = Message.get_weekly_failed_messages(contact_urns_list)
    weekly_unread_messages = Message.get_weekly_unread_messages(contact_urns_list)
    weekly_campaign_events = CampaignEvent.get_campaign_event()
    groups = Group.get_all_groups()

    return render(request, 'report/template_one.html', locals())


def export_to_csv(request, project_id):
    response = HttpResponse(content_type='text/csv')
    datetime_variable = datetime.datetime.now()
    response['Content-Disposition'] = 'attachment; filename="project_groups_%s.csv"' % datetime_variable
    project = Project.objects.get(id=project_id)
    project_groups = project.group.all()
    writer = csv.writer(response)
    writer.writerow(['Group', 'Number of participants'])
    for project_group in project_groups:
        writer.writerow([project_group.name, project_group.count])

    return response


def getdatatest(request):
    data = Voice.get_data(proj="mCrag")
    lss = []
    for d in data:
        contact = d['phone_number']
        lss.append(contact)
    return render(request, 'report/data.html')