from django.test import TestCase
from .models import Contact, Message, Group, Run, Value, Flow, Workspace, Project
from django.utils import timezone
from temba_client.v2 import TembaClient


class DumpTest(TestCase):
    def test_one_plus_one(self):
        self.assertEquals(1 + 1, 2)


class TestWorkspace(TestCase):
    def test_get_rapidpro_workspaces(self):
        Workspace.objects.create(name='Test Workspace', host='hiwa.tmcg.co.ug',
                                 key='1da6d399139139812e2f949a64ce80264184996f')
        workspaces = Workspace.objects.all()
        self.assertEqual(workspaces, Workspace.get_rapidpro_workspaces())


class TestGroup(TestCase):

    def test_add_groups(self):
        client = TembaClient('hiwa.tmcg.co.ug', '1da6d399139139812e2f949a64ce80264184996f')
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


class TestContact(TestCase):
    def test_add_contacts(self):
        client = TembaClient('hiwa.tmcg.co.ug', '1da6d399139139812e2f949a64ce80264184996f')
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


class TestMessage(TestCase):
    def setUp(self):
        group = Group.objects.create(uuid="23fg", name="test-group", count=2)
        Contact.objects.create(uuid="uuid-test", name="name-test", language="language-test", urns="urns-test",
                               groups=group, fields="fields-test", blocked=False, stopped=False,
                               created_on=None, modified_on=None)

    def test_add_messages(self):
        client = TembaClient('hiwa.tmcg.co.ug', '1da6d399139139812e2f949a64ce80264184996f')
        contact = Contact.objects.first()
        message_count = Message.objects.count()
        added_messages = Message.save_messages(contact=contact.uuid, client=client)
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
        Message.objects.create(id=1000, msg_id=1000, broadcast=1, contact=contact, urn="urn-test", channel="channel-test",
                               direction="direction-test", type="type-test", status="status-test",
                               visibility="visibility-test", text="text-test", labels="labels-test", created_on=None,
                               sent_on=None, modified_on=None)
        self.assertEquals(Message.message_exists(qc_mock_message), True)


class TestRun(TestCase):
    def setUp(self):
        group = Group.objects.create(uuid="23fg", name="test-group", count=2)
        Contact.objects.create(uuid="uuid-test", name="name-test", language="language-test", urns="urns-test",
                               groups=group, fields="fields-test", blocked=False, stopped=False,
                               created_on=None, modified_on=None)

    def test_add_runs(self):
        client = TembaClient('hiwa.tmcg.co.ug', '1da6d399139139812e2f949a64ce80264184996f')
        contact = Contact.objects.first()
        run_count = Run.objects.count()
        added_runs = Run.add_runs(contact, client)
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


class TestFlow(TestCase):

    def test_add_steps(self):
        client = TembaClient('hiwa.tmcg.co.ug', '1da6d399139139812e2f949a64ce80264184996f')
        flow_count = Flow.objects.count()
        added_flow = Flow.add_flows(client)
        self.assertEquals(Flow.objects.count(), flow_count + added_flow)


class TestValue(TestCase):
    def setUp(self):
        group = Group.objects.create(uuid="23fg", name="test-group", count=2)
        Contact.objects.create(uuid="uuid-test", name="name-test", language="language-test",
                               urns="urns-test", groups=group, fields="fields-test", blocked=False,
                               stopped=False, created_on=None, modified_on=None)
        c = Contact.objects.first()
        run = Run.objects.create(id=6, run_id=6, responded=False, created_on=timezone.now(), modified_on=timezone.now(),
                                 exit_type='completed', contact=c)
        Value.objects.create(value='testing', run=run)

    def test_add_values(self):
        run_object = Run.objects.first()
        values = Value.objects.all()
        value_count = Value.objects.count()
        added_values = Value.add_values(run_object, values)
        self.assertEquals(Value.objects.count(), value_count + added_values)
