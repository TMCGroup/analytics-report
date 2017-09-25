import datetime
from django.test import TestCase
from django.utils import timezone
from temba_client.v2 import TembaClient
from .models import Contact, Message, Group, Run, Flow, Workspace, Project, Value, Email, Voice
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string


def get_project_groups_list(project_groups):
    project_groups_list = []
    for group in project_groups:
        project_groups_list.append(group)
    return project_groups_list


def get_project_contacts_list(contacts):
    contacts_list = []
    for contact in contacts:
        contacts_list.append(contact)
    return contacts_list


class DumpTest(TestCase):
    def test_one_plus_one(self):
        self.assertEquals(1 + 1, 2)


class WorkspaceTest(TestCase):
    def test_get_rapidpro_workspaces(self):
        Workspace.objects.create(name='Test Workspace', host='hiwa.tmcg.co.ug',
                                 key='f7f5d2ae2e5d37e9e879cc7f8375d1b980b6f3e8')
        workspaces = Workspace.objects.count()
        self.assertEqual(workspaces, Workspace.get_rapidpro_workspaces())


class GroupTest(TestCase):
    def test_add_groups(self):
        client = TembaClient('hiwa.tmcg.co.ug', 'f7f5d2ae2e5d37e9e879cc7f8375d1b980b6f3e8 ')
        group_count = Group.objects.count()
        added_groups = Group.add_groups(client=client)
        self.assertEquals(Group.objects.count(), group_count + added_groups)

    def test_group_exists(self):
        class G(object):
            def __init__(self, name=None, uuid=None, count=None):
                self.name = name
                self.uuid = uuid
                self.count = count

        qc_mock_group = G(name='Test Group', uuid='random number', count=4)
        self.assertEquals(Group.group_exists(qc_mock_group), False)
        Group.objects.create(name='Test Group', uuid='random number', count=4)
        self.assertEquals(Group.group_exists(qc_mock_group), True)


class ContactTest(TestCase):
    def setUp(self):
        group = Group.objects.create(uuid="23fg", name="test-group", count=2)
        Contact.objects.create(uuid="aa221b20-44a8-4b90-9ab9-b6bf5d44d3ef", name="name-test", language="language-test",
                               urns="urns-test",
                               groups=group, fields="fields-test", blocked=False, stopped=False,
                               created_on=datetime.datetime.now(), modified_on=datetime.datetime.now())
        project_one = Project.objects.create(name='Test Project One', lead='Test Lead')
        project_one.group.add(group)

    def test_save_contacts(self):
        client = TembaClient('hiwa.tmcg.co.ug', 'f7f5d2ae2e5d37e9e879cc7f8375d1b980b6f3e8 ')
        contact_count = Contact.objects.count()
        added_contacts = Contact.save_contacts(client=client)
        self.assertEquals(Contact.objects.count(), contact_count + added_contacts)

    def test_contact_exists(self):
        class C(object):
            def __init__(self, id=None, uuid=None, name=None, language=None, urns=None,
                         groups=None, fields=None, blocked=None, stopped=None, created_on=None, modified_on=None):
                self.id = id
                self.uuid = uuid
                self.name = name
                self.language = language
                self.urns = urns
                self.groups = groups
                self.fields = fields
                self.blocked = blocked
                self.stopped = stopped
                self.created_on = created_on
                self.modified_on = modified_on

        qc_mock_contact = C(uuid="uuid-test", name="name-test", language="language-test", urns="urns-test",
                            groups=[], fields="fields-test", blocked=False, stopped=False, created_on=None,
                            modified_on=None)
        self.assertEquals(Contact.contact_exists(qc_mock_contact), False)
        Contact.objects.create(uuid="uuid-test", name="name-test", language="language-test", urns="urns-test",
                               groups=[], fields="fields-test", blocked=False, stopped=False,
                               created_on=None, modified_on=None)
        self.assertEquals(Contact.contact_exists(qc_mock_contact), True)

    def test_get_all_contacts(self):
        contacts = Contact.objects.all()
        # self.assertQuerysetEqual(Contact.get_all_contacts(), ['<Contact: urns-test>'])
        self.assertQuerysetEqual(Contact.get_all_contacts(), map(repr, contacts))

    def test_get_project_contacts(self):
        project = Project.objects.first()
        project_groups = project.group.all()
        project_groups_list = get_project_groups_list(project_groups)
        contacts = Contact.objects.all()
        self.assertQuerysetEqual(Contact.get_project_contacts(project_groups_list), map(repr, contacts))

    def test_get_project_contacts_count(self):
        pass


class MessageTest(TestCase):
    def setUp(self):
        group = Group.objects.create(uuid="23fg", name="test-group", count=2)
        contact = Contact.objects.create(uuid="test-uuid", name="name-test", language="language-test",
                                         urns="urns-test",
                                         groups=group, fields="fields-test", blocked=False, stopped=False,
                                         created_on=None, modified_on=None)
        project_one = Project.objects.create(name='Test Project One', lead='Test Lead')
        project_one.group.add(group)
        Message.objects.create(id=1, msg_id=1001, broadcast=1, contact=contact, urn="urns-test",
                               channel="channel-test",
                               direction="in", type="type-test", status="failed",
                               visibility="visibility-test", text="text-test", labels="labels-test",
                               created_on=(datetime.datetime.now() - datetime.timedelta(1)),
                               sent_on=datetime.datetime.now(),
                               modified_on=(datetime.datetime.now() - datetime.timedelta(1)))
        Message.objects.create(id=2, msg_id=1002, broadcast=1, contact=contact, urn="urns-test",
                               channel="channel-test",
                               direction="out", type="type-test", status="delivered",
                               visibility="visibility-test", text="text-test", labels="labels-test",
                               created_on=datetime.datetime.now(),
                               sent_on=datetime.datetime.now(),
                               modified_on=(datetime.datetime.now() - datetime.timedelta(1)))

    def test_save_messages(self):
        client = TembaClient('hiwa.tmcg.co.ug', 'f7f5d2ae2e5d37e9e879cc7f8375d1b980b6f3e8 ')
        message_count = Message.objects.count()
        contacts = Contact.objects.all()
        added_messages = 0
        for contact in contacts:
            added_messages = + Message.save_messages(client=client, contact=contact)

        self.assertEquals(Message.objects.count(), message_count + added_messages)

    def test_message_exists(self):
        class M(object):
            def __init__(self, id=None, msg_id=None, folder=None, broadcast=None, contact=None, urn=None, channel=None,
                         direction=None, type=None, status=None, visibility=None, text=None, labels=None,
                         created_on=None, sent_on=None, modified_on=None):
                self.id = id
                self.msg_id = msg_id
                self.folder = folder
                self.broadcast = broadcast
                self.contact = contact
                self.urn = urn
                self.channel = channel
                self.direction = direction
                self.type = type
                self.status = status
                self.visibility = visibility
                self.text = text
                self.labels = labels
                self.sent_on = sent_on
                self.created_on = created_on
                self.modified_on = modified_on

        contact = Contact.objects.first()
        qc_mock_message = M(id=1000, msg_id=1000, broadcast=1, contact=contact, urn="urn-test", channel="channel-test",
                            direction="direction-test", type="type-test", status="status-test",
                            visibility="visibility-test", text="text-test", labels="labels-test", created_on=None,
                            sent_on=None, modified_on=None)
        self.assertEquals(Message.message_exists(qc_mock_message), False)
        Message.objects.create(id=1000, msg_id=1000, broadcast=1, contact=contact, urn="urn-test",
                               channel="channel-test",
                               direction="direction-test", type="type-test", status="status-test",
                               visibility="visibility-test", text="text-test", labels="labels-test", created_on=None,
                               sent_on=None, modified_on=None)
        self.assertEquals(Message.message_exists(qc_mock_message), True)

    def test_get_all_specific_incoming_messages(self):
        project = Project.objects.first()
        project_groups = project.group.all()
        project_groups_list = []
        for group in project_groups:
            project_groups_list.append(group)
        contacts = Contact.objects.all()
        contacts_list = []
        for contact in contacts:
            contacts_list.append(contact)
        incoming_messages = Message.objects.filter(direction='in').all()
        self.assertQuerysetEqual(Message.get_all_specific_incoming_messages(contacts_list),
                                 map(repr, incoming_messages))

    def test_get_weekly_failed_messages(self):
        contacts = Contact.objects.all()
        contacts_list = get_project_contacts_list(contacts)
        date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
        weekly_failed_messages = Message.objects.filter(status="failed", direction="out",
                                                        sent_on__range=(date_diff, datetime.datetime.now())).all()
        self.assertQuerysetEqual(Message.get_weekly_failed_messages(contacts_list), map(repr, weekly_failed_messages),
                                 msg=False, transform=repr)

    def test_get_weekly_hanging_messages(self):
        contacts = Contact.objects.all()
        contacts_list = get_project_contacts_list(contacts)
        date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
        weekly_failed_messages = Message.objects.filter(direction="out",
                                                        sent_on__range=(date_diff, datetime.datetime.now())).exclude(
            status__in=['delivered', 'failed', 'handled', 'queued']).all()
        self.assertQuerysetEqual(Message.get_weekly_hanging_messages(contacts_list), map(repr, weekly_failed_messages),
                                 msg=False, transform=repr)

    def test_get_weekly_delivered_messages(self):
        contacts = Contact.objects.all()
        contacts_list = get_project_contacts_list(contacts)
        date_diff = datetime.datetime.now() - datetime.timedelta(days=7)
        weekly_failed_messages = Message.objects.filter(status="delivered", direction="out",
                                                        sent_on__range=(date_diff, datetime.datetime.now())).all()
        self.assertQuerysetEqual(Message.get_weekly_delivered_messages(contacts_list),
                                 map(repr, weekly_failed_messages),
                                 msg=False, transform=repr)


class RunTest(TestCase):
    def setUp(self):
        group = Group.objects.create(uuid="23fg", name="test-group", count=2)
        Contact.objects.create(uuid="aa221b20-44a8-4b90-9ab9-b6bf5d44d3ef", name="name-test", language="language-test",
                               urns="urns-test",
                               groups=group, fields="fields-test", blocked=False, stopped=False,
                               created_on=None, modified_on=None)
        Flow.objects.create(uuid='788ghh', name='flow-test', expires=1, created_on=datetime.datetime.now())

    def test_add_runs(self):
        client = TembaClient('hiwa.tmcg.co.ug', 'f7f5d2ae2e5d37e9e879cc7f8375d1b980b6f3e8 ')
        run_count = Run.objects.count()
        added_runs = Run.add_runs(client)
        self.assertEquals(Run.objects.count(), run_count + added_runs)

    def test_run_exists(self):
        class T(object):
            def __init__(self, id=None, run_id=None, responded=None, created_on=None, modified_on=None, exit_type=None,
                         contact=None):
                self.id = run_id
                self.run_id = run_id
                self.responded = responded
                self.created_on = created_on
                self.modified_on = modified_on
                self.exit_type = exit_type
                self.contact = contact

        contact_object = Contact.objects.first()
        rapidpro_mock_run = T(id=6, run_id=6, responded=False, created_on=timezone.now(), modified_on=timezone.now(),
                              exit_type='completed', contact=contact_object)
        self.assertEquals(Run.run_exists(rapidpro_mock_run), False)
        Run.objects.create(id=6, run_id=6, responded=False, created_on=timezone.now(), modified_on=timezone.now(),
                           exit_type='completed', contact=contact_object)
        self.assertEquals(Run.run_exists(rapidpro_mock_run), True)


class FlowTest(TestCase):
    def setUp(self):
        Flow.objects.create(uuid='788ghh', name='flow-test', expires=1, created_on=datetime.datetime.now())

    def test_add_flows(self):
        client = TembaClient('hiwa.tmcg.co.ug', 'f7f5d2ae2e5d37e9e879cc7f8375d1b980b6f3e8 ')
        flow = Flow.objects.first()
        flow_count = Flow.objects.count()
        added_flow = Flow.add_flows(client)
        self.assertEquals(Flow.objects.count(), flow_count + added_flow)


class ProjectTest(TestCase):
    def setUp(self):
        group_one = Group.objects.create(name='Test Group One', uuid='random number one', count=1)
        group_two = Group.objects.create(name='Test Group Two', uuid='random number two', count=2)
        project = Project.objects.create(name='Test Project', lead='Test Lead')
        project.group.add(group_one, group_two)

    def test_get_project(self):
        project = Project.objects.filter(name='Test Project')
        self.assertEquals(project.count(), Project.get_project(name='Test Project').count())

    def test_get_all_projects(self):
        projects = Project.objects.filter(active=True).all()
        self.assertEquals(projects.count(), Project.get_all_projects().count())


class EmailTest(TestCase):
    def setUp(self):
        group_one = Group.objects.create(name='Test Group One', uuid='random number one', count=1)
        group_two = Group.objects.create(name='Test Group Two', uuid='random number two', count=2)
        project_one = Project.objects.create(name='Test Project One', lead='Test Lead')
        project_one.group.add(group_one, group_two)
        project_two = Project.objects.create(name='Test Project Two', lead='Test Lead')
        project_two.group.add(group_one)
        email_one = Email.objects.create(name="Test Email One", email_address="test1@email.com")
        email_one.project.add(project_one)
        email_one.project.add(project_two)
        email_two = Email.objects.create(name="Test Email Two", email_address="test2@email.com")
        email_two.project.add(project_one)

    def test_get_project_mailing_list(self):
        project = Project.objects.get(name='Test Project One')
        mailing_list = ["test1@email.com", "test2@email.com"]
        mailing_list_test = Email.get_project_mailing_list(project.id)
        self.assertEquals(mailing_list, mailing_list_test)

    def test_get_report_emails(self):
        project = Project.objects.get(name='Test Project One')
        emails = Email.objects.filter(project__name=project.name).all()
        report_datetime = datetime.datetime.now()
        emailing_list = Email.get_project_mailing_list(project.id)
        email_subject = '%s Weekly ( %s ) Report' % (project.name, report_datetime)
        email_body = render_to_string('report/report_email_body.html')
        email_message = EmailMultiAlternatives(email_subject, email_body, settings.EMAIL_HOST_USER, emailing_list)
        self.assertEquals(email_message.recipients(), Email.get_report_emails(project_id=project.id).recipients())


class VoiceTest(TestCase):
    def setUp(self):
        group_one = Group.objects.create(name='Test Group One', uuid='random number one', count=1)
        project_one = Project.objects.create(name='SMS MAAMA', lead='Test Lead')
        project_one.group.add(group_one)

    def test_get_data(self):
        project = Project.objects.first()
        voice_count = Voice.objects.count()
        Voice.get_data(project_name=project.name)
        self.assertGreaterEqual(Voice.objects.count(), voice_count, msg=True)

# class ValueTest(TestCase):
#     def setUp(self):
#         group = Group.objects.create(uuid="23fg", name="test-group", count=2)
#         Contact.objects.create(uuid="uuid-test", name="name-test", language="language-test",
#                                urns="urns-test", groups=group, fields="fields-test", blocked=False,
#                                stopped=False, created_on=None, modified_on=None)
#         c = Contact.objects.first()
#         run = Run.objects.create(id=6, run_id=6, responded=False, created_on=timezone.now(), modified_on=timezone.now(),
#                                  exit_type='completed', contact=c,
#                                  values={"color": {"value": "blue", "category": "Blue",
#                                                    "node":
#                                                        "fc32aeb0-ac3e-42a8-9ea7-10248"
#                                                        "fdf52a1",
#                                                    "time": "2015-11-11T13:03:51.63566"
#                                                            "2Z"}, "reason": {
#                                      "value": "Because it's the color of sky", "category": "All Responses",
#                                      "node": "4c9cb68d-474f-4b9a-b65e-c2aa593a3466",
#                                      "time": "2015-11-11T13:05:57.576056Z"}})
#
#     def test_add_values(self):
#         run = Run.objects.first()
#         value_count = Value.objects.count()
#         added_values = Value.add_values(run, run.values)
#         self.assertEquals(Value.objects.count(), value_count + added_values)
