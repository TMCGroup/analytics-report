import csv
import datetime
import random
import time
from StringIO import StringIO
import pytz
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string

from reports.templatetags import report_tags
from .models import Contact, Message, Group, CampaignEvent, Project, Voice, Email
from nvd3 import pieChart, cumulativeLineChart, discreteBarChart, scatterChart
from django.views.decorators.cache import cache_page
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import letter, cm, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ValidationError
from django.conf import settings

tz = 'Africa/Kampala'


class EmailAuthenticationForm(AuthenticationForm):
    def clean_username(self):
        username = self.data['username']
        if '@' in username:
            try:
                username = User.objects.get(email=username).username
            except ObjectDoesNotExist:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
        return username


@cache_page(60 * 15)
def dashboard(request):
    projects = Project.get_all_projects()
    groups = Group.get_all_groups()
    groups_list = []
    for group in groups:
        groups_list.append(group.name)

    contacts = Contact.get_all_contacts()
    registered_contacts = Contact.get_all_registered_contacts(groups_list)
    registered_contacts_list = []
    for contact in registered_contacts:
        registered_contacts_list.append(contact.urns)
    unregistered_contacts = Contact.get_all_unregistered_contacts(groups_list)
    unregistered_contacts_list = []
    for contact in unregistered_contacts:
        unregistered_contacts_list.append(contact.urns)
    percentage_registered_contacts = Contact.get_all_contacts_percentage(registered_contacts.count(), groups_list)
    percentage_unregistered_contacts = Contact.get_all_contacts_percentage(unregistered_contacts.count(), groups_list)
    incoming_messages = Message.get_all_incoming_messages()
    outgoing_messages = Message.get_all_outgoing_messages()
    messages_cost = Message.get_cost_of_incoming_messages(incoming_messages.count()) + Message. \
        get_cost_of_outgoing_messages(outgoing_messages.count())
    registered_incoming_messages = Message.get_all_specific_incoming_messages(registered_contacts_list)
    unregistered_incoming_messages = Message.get_all_specific_incoming_messages(unregistered_contacts_list)
    # unregistered_incoming_messages = incoming_messages.count() - registered_incoming_messages.count()
    unregistered_incoming_messages_cost = Message.get_cost_of_incoming_messages(unregistered_incoming_messages.count())
    registered_incoming_messages_cost = Message.get_cost_of_incoming_messages(registered_incoming_messages.count())

    registered_contacts_set = registered_contacts.count()
    unregistered_contacts_set = unregistered_contacts.count()

    x1_data = ['Registered Contacts', 'Unregistered Contacts']
    y1_data = [registered_contacts_set, unregistered_contacts_set]

    color_list = ['#008000', '#DC143C']
    extra_serie = {
        "tooltip": {"y_start": "", "y_end": " cal"},
        "color_list": color_list
    }
    chart1_data = {'x': x1_data, 'y1': y1_data, 'extra1': extra_serie}
    chart1_type = "pieChart"
    chart1_container = 'piechart_container'  # container name
    extra = {
        'x_is_date': False,
        'x_axis_format': '',
        'tag_script_js': True,
        'jquery_on_ready': False,
        'donut': True,
        'donutRatio': 0.35,
    }

    return render(request, 'report/dashboard.html', locals())


def dashboard_nav(request):
    projects = Project.get_all_projects()
    return render(request, 'adminlte/lib/_main_sidebar.html', locals())


@cache_page(60 * 15)
def report_template_one(request, project_id):
    projects = Project.get_all_projects()
    project = Project.objects.get(id=project_id)
    project_groups = project.group.all()
    top_five_project_groups = project.group.all().order_by('-count')[:5]
    project_groups_count = project.group.count()
    project_group_list = Project.get_project(name=project.name)
    voice_platform = Voice.get_weekly_voice_interaction(project=project)
    top_five_voice_interactions = voice_platform.order_by('-created_on')[:5]

    group_list = []
    for group in project_groups:
        group_list.append(group.name)

    contacts = Contact.get_project_contacts(project_groups_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_groups_list=group_list)
    top_five_weekly_contacts = weekly_contacts.order_by('-created_on')[:5]
    weekly_contacts_value_list = Contact.get_all_project_contacts_value_list(project_groups_list=group_list)
    weekly_contact_percentage = Contact.get_project_contacts_percentage(contact_variable=weekly_contacts.count(),
                                                                        project_groups_list=group_list)
    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)

    number_of_contacts = len(contact_urns_list)
    incoming_messages = Message.get_all_project_incoming_messages(contact_urns_list)
    outgoing_messages = Message.get_all_project_outgoing_messages(contact_urns_list)
    project_messages_cost = Message.get_cost_of_incoming_messages(incoming_messages.count()) + Message. \
        get_cost_of_outgoing_messages(outgoing_messages.count())
    weekly_sent_messages = Message.get_weekly_sent_messages(contact_urns_list)
    weekly_delivered_messages = Message.get_weekly_delivered_messages(contact_urns_list)
    weekly_failed_messages = Message.get_weekly_failed_messages(contact_urns_list)
    top_five_weekly_failed_messages = weekly_failed_messages.order_by('-sent_on')[:5]
    weekly_hanging_messages = Message.get_weekly_hanging_messages(contact_urns_list)
    top_five_weekly_hanging_messages = weekly_hanging_messages.order_by('-sent_on')[:5]
    weekly_campaign_events = CampaignEvent.get_campaign_event()
    groups = Group.get_all_groups()
    percentage_weekly_delivered_messages = Message.get_project_weekly_messages_percentage(
        message_variable=weekly_delivered_messages.count(), contacts_list=contact_urns_list)
    percentage_weekly_hanging_messages = Message.get_project_weekly_messages_percentage(
        message_variable=weekly_hanging_messages.count(), contacts_list=contact_urns_list)
    percentage_weekly_failed_messages = Message.get_project_weekly_messages_percentage(
        message_variable=weekly_failed_messages.count(), contacts_list=contact_urns_list)

    weekly_delivered_messages_set = weekly_delivered_messages.count()
    weekly_failed_messages_set = weekly_failed_messages.count()
    weekly_hanging_messages_set = weekly_hanging_messages.count()

    x1_data = ['Delivered', 'Failed', 'Hanging']
    y1_data = [weekly_delivered_messages_set, weekly_failed_messages_set, weekly_hanging_messages_set]

    color_list = ['#008000', '#DC143C', '#FFD700']
    extra_serie = {
        "tooltip": {"y_start": "", "y_end": " messages"},
        "color_list": color_list
    }
    chart1_data = {'x': x1_data, 'y1': y1_data, 'extra1': extra_serie}
    chart1_type = "pieChart"
    chart1_container = 'piechart_container'  # container name
    extra = {
        'x_is_date': False,
        'x_axis_format': '',
        'tag_script_js': True,
        'jquery_on_ready': False,
    }

    x2_data = []
    x2_data1 = []
    for i in range(0, 7):
        x2_data.append(datetime.date.today() - datetime.timedelta(days=i))
        x2_data1.append(str(datetime.date.today() - datetime.timedelta(days=i)))

    x2data = []
    for given_date in x2_data:
        start_time = int(time.mktime(given_date.timetuple()) * 1000)
        x2data.append(start_time)
        # nb_element = 100
        # x2data = range(nb_element)
        # x2data = map(lambda x: start_time + x * 1000000000, x2data)

    y2_data = []
    for j in x2_data:
        y2_data.append(weekly_contacts.filter(created_on__date=j).count())

    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra2_serie = {
        "tooltip": {"y_start": "", "y_end": " contacts"},
        "date_format": tooltip_date
    }
    chart2_data = {'x': x2data,
                   'name2': 'contacts', 'y2': y2_data, 'extra2': extra2_serie
                   }
    chart2_type = "lineChart"
    chart2_container = 'linechart_container'  # container name
    extra2 = {
        'x_is_date': True,
        'x_axis_format': '',
        'tag_script_js': True,
        'jquery_on_ready': False,
    }
    email= Email.get_report_emails(project.id)

    return render(request, 'report/template_one.html', locals())


@cache_page(60 * 15)
def view_all_project_groups(request, project_id):
    projects = Project.get_all_projects()
    project = Project.objects.get(id=project_id)
    project_groups = project.group.all()

    return render(request, 'report/project_groups.html', locals())


@cache_page(60 * 15)
def view_all_project_weekly_contacts(request, project_id):
    projects = Project.get_all_projects()
    project = Project.objects.get(id=project_id)
    project_groups = project.group.all()
    group_list = []
    for group in project_groups:
        group_list.append(group.name)

    contacts = Contact.get_project_contacts(project_groups_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_groups_list=group_list)

    return render(request, 'report/weekly_project_contacts.html', locals())


@cache_page(60 * 15)
def view_all_project_contacts(request, project_id):
    projects = Project.get_all_projects()
    project = Project.objects.get(id=project_id)
    project_groups = project.group.all()
    group_list = []
    for group in project_groups:
        group_list.append(group.name)

    contacts = Contact.get_project_contacts(project_groups_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_groups_list=group_list)

    return render(request, 'report/project_contacts.html', locals())


@cache_page(60 * 15)
def view_all_project_weekly_failed_messages(request, project_id):
    projects = Project.get_all_projects()
    project = Project.objects.get(id=project_id)
    project_groups = project.group.all()
    group_list = []
    for group in project_groups:
        group_list.append(group.name)

    contacts = Contact.get_project_contacts(project_groups_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_groups_list=group_list)
    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)

    weekly_failed_messages = Message.get_weekly_failed_messages(contact_urns_list)

    return render(request, 'report/weekly_project_failed_messages.html', locals())


@cache_page(60 * 15)
def view_all_project_weekly_hanging_messages(request, project_id):
    projects = Project.get_all_projects()
    project = Project.objects.get(id=project_id)
    project_groups = project.group.all()
    group_list = []
    for group in project_groups:
        group_list.append(group.name)

    contacts = Contact.get_project_contacts(project_groups_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_groups_list=group_list)
    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)

    weekly_hanging_messages = Message.get_weekly_hanging_messages(contact_urns_list)

    return render(request, 'report/weekly_project_hanging_messages.html', locals())


def view_all_project_weekly_voice_interactions(request, project_id):
    project = Project.objects.get(id=project_id)
    voice_interactions = Voice.objects.filter(project=project).all()
    return render(request, 'report/weekly_project_voice_interactions.html', locals())


@cache_page(60 * 15)
def export_to_csv(request, project_id):
    project = Project.objects.get(id=project_id)
    voice_platform = Voice.objects.filter(project=project).all()
    datetime_variable = datetime.datetime.now()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s_report_%s.csv"' % (project.name, datetime_variable)
    project_groups = project.group.all()

    group_list = []
    for group in project_groups:
        group_list.append(group.name)

    contacts = Contact.get_project_contacts(project_groups_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_groups_list=group_list)

    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)

    number_of_contacts = len(contact_urns_list)
    incoming_messages = Message.get_all_project_incoming_messages(contact_urns_list)
    outgoing_messages = Message.get_all_project_outgoing_messages(contact_urns_list)
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
    writer.writerow(['Contact Number', 'Contact Name', 'Created on / Joined on'])
    for contact in contacts:
        contact_groups = [contact_groups for contact_groups in report_tags.clean(contact.groups)]
        writer.writerow([contact.urns, contact.name, contact.created_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['%s Weekly Joined Contacts' % project.name])
    writer.writerow(['Contact Number', 'Contact Name', 'Group', 'Created on / Joined on'])
    for contact in weekly_contacts:
        contact_groups = [contact_groups for contact_groups in report_tags.clean(contact.groups)]
        writer.writerow([contact.urns, contact.name, contact_groups, contact.created_on])
    writer.writerow([])
    writer.writerow([])

    if number_of_contacts > 0:
        writer.writerow(['%s Message Summary' % project.name])
        writer.writerow(['Description', 'Number of Messages'])
        writer.writerow(['Incoming Messages', incoming_messages.count()])
        writer.writerow(['Outgoing Messages', outgoing_messages.count()])
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
    for call in voice_platform:
        writer.writerow([call.contact, call.reason, call.created_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow([])

    return response


def generate_pdf_weekly_report(request, project_id):
    buffer = StringIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=20, bottomMargin=20)
    report = []

    project = Project.objects.get(id=project_id)
    project_groups = project.group.all()
    top_five_project_groups = project.group.all().order_by('-count')[:5]
    project_groups_count = project.group.count()
    project_group_list = Project.get_project(name=project.name)
    voice_platform = Voice.get_weekly_voice_interaction(project=project)

    group_list = []
    for group in project_groups:
        group_list.append(group.name)

    contacts = Contact.get_project_contacts(project_groups_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_groups_list=group_list)
    weekly_contact_percentage = Contact.get_project_contacts_percentage(contact_variable=weekly_contacts.count(),
                                                                        project_groups_list=group_list)
    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)

    weekly_sent_messages = Message.get_weekly_sent_messages(contact_urns_list)
    weekly_delivered_messages = Message.get_weekly_delivered_messages(contact_urns_list)
    weekly_failed_messages = Message.get_weekly_failed_messages(contact_urns_list)
    weekly_hanging_messages = Message.get_weekly_hanging_messages(contact_urns_list)
    groups = Group.get_all_groups()
    percentage_weekly_delivered_messages = Message.get_project_weekly_messages_percentage(
        message_variable=weekly_delivered_messages.count(), contacts_list=contact_urns_list)
    percentage_weekly_hanging_messages = Message.get_project_weekly_messages_percentage(
        message_variable=weekly_hanging_messages.count(), contacts_list=contact_urns_list)
    percentage_weekly_failed_messages = Message.get_project_weekly_messages_percentage(
        message_variable=weekly_failed_messages.count(), contacts_list=contact_urns_list)

    logo = "reports/static/images/logo.jpg"
    project_name = project.name
    report_title = "%s Weekly Report" % project.name
    prepared_by = "Faith Nassiwa"
    start_date = datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today() - datetime.timedelta(days=1)
    this_day = datetime.datetime.now(pytz.timezone('Africa/Kampala')).strftime('%Y-%m-%d %H:%M %Z')

    im = Image(logo, 3 * inch, 1.5 * inch)
    table_data = [[im]]
    t = Table(table_data)
    report.append(t)
    report.append(Spacer(1, 12))
    styles = getSampleStyleSheet()
    # styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT))
    ptext = '<font size=18><b>%s</b></font>' % report_title
    report.append(Paragraph(ptext, styles["Normal"]))
    report.append(Spacer(1, 12))
    ptext = '<font size=12> Report Date: %s - %s</font>' % (start_date, end_date)
    report.append(Paragraph(ptext, styles["Normal"]))
    ptext = '<font size=12>Report generated on: %s</font>' % this_day
    report.append(Paragraph(ptext, styles["Normal"]))
    ptext = '<font size=12> Compiled By: %s</font>' % prepared_by
    report.append(Paragraph(ptext, styles["Normal"]))

    report.append(Spacer(1, 12))
    report.append(Spacer(1, 12))
    ptext = '<font size=12> %s has a total of %s contacts. ' \
            '<br/>%s newly enrolled contacts from last week. ' \
            '<br/>%s messages were sent out last week. ' \
            '<br/>%s delivered. ' \
            '<br/>%s hanging. ' \
            '<br/>%s failed.</font>' \
            % (project.name, contacts.count(), weekly_contacts.count(), weekly_sent_messages.count(),
               percentage_weekly_delivered_messages, percentage_weekly_hanging_messages,
               percentage_weekly_failed_messages)
    report.append(Paragraph(ptext, styles["Normal"]))
    ptext = '<font size=12>Below is a summary of message delivery status.</font>'
    report.append(Paragraph(ptext, styles["Normal"]))
    report.append(Spacer(1, 12))
    message_titles = ['Delivered', 'Hanging', 'Failed to send']
    data = [message_titles]
    colwidths = (150, 150, 150)
    data.append([weekly_delivered_messages.count(), weekly_hanging_messages.count(), weekly_failed_messages.count()])

    t = Table(data, colwidths, style=[('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                      ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
                                      ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                                      ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                      ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                                      ])

    report.append(t)
    report.append(Spacer(1, 12))

    doc.build(report)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def send_csv_attachment_email(request, project_id):
    buffer = StringIO()
    project = Project.objects.get(id=project_id)
    datetime_variable = datetime.date.today()
    project_groups = project.group.all()
    voice_platform = Voice.objects.filter(project=project).all()
    group_list = []
    for group in project_groups:
        group_list.append(group.name)
    contacts = Contact.get_project_contacts(project_groups_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_groups_list=group_list)

    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)

    number_of_contacts = len(contact_urns_list)
    incoming_messages = Message.get_all_project_incoming_messages(contact_urns_list)
    outgoing_messages = Message.get_all_project_outgoing_messages(contact_urns_list)
    weekly_sent_messages = Message.get_weekly_sent_messages(contact_urns_list)
    weekly_delivered_messages = Message.get_weekly_delivered_messages(contact_urns_list)
    weekly_failed_messages = Message.get_weekly_failed_messages(contact_urns_list)
    weekly_hanging_messages = Message.get_weekly_hanging_messages(contact_urns_list)
    campaign_events = CampaignEvent.get_campaign_event()
    groups = Group.get_all_groups()

    writer = csv.writer(buffer)
    writer.writerow([])
    writer.writerow(['%s Report' % project.name])
    writer.writerow(['Generated on: %s' % datetime_variable])
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
    writer.writerow(['Contact Number', 'Contact Name', 'Created on / Joined on'])
    for contact in contacts:
        writer.writerow([contact.urns, contact.name, contact.created_on])
    writer.writerow([])
    writer.writerow([])

    writer.writerow(['%s Weekly Enrolled Contacts' % project.name])
    writer.writerow(['Contact Number', 'Contact Name', 'Created on / Joined on'])
    for contact in weekly_contacts:
        writer.writerow([contact.urns, contact.name, contact.created_on])
    writer.writerow([])
    writer.writerow([])

    if number_of_contacts > 0:
        writer.writerow(['%s Message Summary' % project.name])
        writer.writerow(['Description', 'Number of Messages'])
        writer.writerow(['Incoming Messages', incoming_messages.count()])
        writer.writerow(['Outgoing Messages', outgoing_messages.count()])
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

    writer.writerow(['Contact Number', 'Reason for call', 'Date'])
    for call in voice_platform:
        writer.writerow([call.contact, call.reason, call.created_on])
    writer.writerow([])
    writer.writerow([])
    writer.writerow([])

    csv_file = buffer.getvalue()
    buffer.close()

    return csv_file


def send_report_email(request, project_id):
    project = Project.objects.get(id=project_id)
    report_datetime = datetime.datetime.now()
    pdf = generate_pdf_weekly_report(request, project.id)
    csv_file = send_csv_attachment_email(request, project.id)
    email = Email.get_report_emails(project.id)
    email.attach('%s_report_%s.pdf' % (project.name, report_datetime), pdf, 'application/pdf')
    email.attach('%s_report_%s.csv' % (project.name, report_datetime), csv_file, 'text/csv')
    email.content_subtype = "html"
    email.send()

    return HttpResponse('email(s) sent')

