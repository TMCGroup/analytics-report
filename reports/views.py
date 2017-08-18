# noinspection PyUnresolvedReferences
import csv
import datetime
import StringIO
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from reports.templatetags import report_tags
from .models import Contact, Message, Group, CampaignEvent, Project, Voice, Email
from nvd3 import pieChart, cumulativeLineChart, discreteBarChart, scatterChart
from django.views.decorators.cache import cache_page


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
    #unregistered_incoming_messages = incoming_messages.count() - registered_incoming_messages.count()
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
    voice_platform = Voice.objects.filter(project=project).all()
    top_five_voice_interactions = voice_platform.order_by('-date')[:5]

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
    }

    x2_data = []
    for i in range(0, 7):
        x2_data.append(datetime.date.today() - datetime.timedelta(days=i))

    y2_data = []
    for j in range(0, weekly_contacts.count()):
        y2_data.append(j * (round(float(weekly_contacts.count()/5), 0)))

    extra2_serie = {
        "tooltip": {"y_start": "", "y_end": " cal"},
    }
    chart2_data = {'x': x1_data, 'y1': y1_data, 'extra1': extra2_serie}
    chart2_type = "lineChart"
    chart2_container = 'linechart_container'  # container name
    extra2 = {
        'x_is_date': True,
        'x_axis_format': '',
        'tag_script_js': True,
        'jquery_on_ready': False,
    }

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


def report_template_one_pdf(request, project_id):
    project = Project.objects.get(id=project_id)
    project_groups = project.group.all()
    project_groups_count = project.group.count()
    project_group_list = Project.get_project(name=project.name)
    voice_platform = Voice.objects.filter(project=project).all()

    group_list = []

    for group in project_groups:
        group_list.append(group.name)

    contacts = Contact.get_project_contacts(project_groups_list=group_list)
    weekly_contacts = Contact.get_weekly_project_contacts(project_groups_list=group_list)
    contact_counts = Contact.get_project_contacts_count(project_groups_list=group_list)
    weekly_contacts_value_list = Contact.get_all_project_contacts_value_list(project_groups_list=group_list)
    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)

    number_of_contacts = len(contact_urns_list)
    weekly_sent_messages = Message.get_weekly_sent_messages(contact_urns_list)
    weekly_delivered_messages = Message.get_weekly_delivered_messages(contact_urns_list)
    weekly_failed_messages = Message.get_weekly_failed_messages(contact_urns_list)
    weekly_hanging_messages = Message.get_weekly_hanging_messages(contact_urns_list)
    weekly_unread_messages = Message.get_weekly_unread_messages(contact_urns_list)
    weekly_campaign_events = CampaignEvent.get_campaign_event()

    return render(request, 'report/my-pdf.html', locals())


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
    writer.writerow(['Contact Number', 'Contact Name', 'Group', 'Created on / Joined on'])
    for contact in contacts:
        contact_groups = [contact_groups for contact_groups in report_tags.clean(contact.groups)]
        writer.writerow([contact.urns, contact.name, contact_groups, contact.created_on])
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


@cache_page(60 * 15)
def send_csv_attachment_email(request, project_id):
    csv_file = StringIO.StringIO()

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
        writer.writerow([contact.urns, contact.name,
                         (contact_groups for contact_groups in report_tags.clean(contact.groups)), contact.created_on])
    writer.writerow([])
    writer.writerow([])

    writer.writerow(['%s Weekly Enrolled Contacts' % project.name])
    writer.writerow(['Contact Number', 'Contact Name', 'Group(s)', 'Created on / Joined on'])
    for contact in weekly_contacts:
        writer.writerow([contact.urns, contact.name,
                         (contact_groups for contact_groups in report_tags.clean(contact.groups)), contact.created_on])
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

    # Email.email_report(csv_file=csv_file.getvalue(), project_id=project.id)
    # subject = '%s Weekly Report %s' % (project.name, datetime_variable)
    # email = EmailMessage(
    #     subject,
    #     'Please find attached a sample of the csv file attachment, voice data and pdf view to be included '
    #     'during course of the week.',
    #     settings.EMAIL_HOST_USER,
    #     ['faithnassiwa@gmail.com'],
    # )
    email = Email.get_report_emails(project_id=project.id)
    email.attach('%s_report_%s.csv' % (project.name, datetime_variable), csv_file.getvalue(), 'text/csv')
    email.send()
    return HttpResponse("Email Sent")


def get_data_test(request):
    data = Voice.get_data(project_name="mCrag")
    lss = []
    for d in data:
        contact = d['phone_number']
        lss.append(contact)

    return render(request, 'report/data.html', locals())


def demo_piechart(request, project_id):
    """
    pieChart page
    """
    project = Project.objects.get(id=project_id)
    project_groups = project.group.all()
    project_groups_count = project.group.count()
    project_group_list = Project.get_project(name=project.name)
    group_list = []

    for group in project_groups:
        group_list.append(group.name)

    contacts = Contact.get_project_contacts(project_groups_list=group_list)
    contact_urns_list = []
    for contact in contacts:
        contact_urns_list.append(contact.urns)

    weekly_sent_messages = Message.get_weekly_sent_messages(contact_urns_list)
    weekly_delivered_messages = Message.get_weekly_delivered_messages(contact_urns_list)
    weekly_failed_messages = Message.get_weekly_failed_messages(contact_urns_list)
    weekly_hanging_messages = Message.get_weekly_hanging_messages(contact_urns_list)

    weekly_delivered_messages_set = weekly_delivered_messages.count()
    weekly_failed_messages_set = weekly_failed_messages.count()
    weekly_hanging_messages_set = weekly_hanging_messages.count()

    xdata = ['Delivered', 'Failed', 'Hanging']
    ydata = [weekly_delivered_messages_set, weekly_failed_messages_set, weekly_hanging_messages_set]
    # xdata = ["Apple", "Apricot", "Avocado", "Banana", "Boysenberries",
    #          "Blueberries", "Dates", "Grapefruit", "Kiwi", "Lemon"]
    # ydata = [52, 48, 160, 94, 75, 71, 490, 82, 46, 17]

    color_list = ['#5d8aa8', '#e32636', '#efdecd', '#ffbf00', '#ff033e', '#a4c639',
                  '#b2beb5', '#8db600', '#7fffd4', '#ff007f', '#ff55a3', '#5f9ea0']
    extra_serie = {
        "tooltip": {"y_start": "", "y_end": " cal"},
        "color_list": color_list
    }
    chartdata = {'x': xdata, 'y1': ydata, 'extra1': extra_serie}
    charttype = "pieChart"
    chartcontainer = 'piechart_container'  # container name

    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    return render(request, 'report/piechart.html', data)
