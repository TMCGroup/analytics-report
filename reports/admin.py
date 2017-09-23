from django.contrib import admin
from .models import Contact, Group, Run, Flow, Message, Workspace, Project, CampaignEvent, Campaign, Voice, Email, Value


class EmailAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_address', 'show_projects')

    search_fields = ['name', 'show_projects']

    def show_projects(self, obj):
        return "\n".join([a.name for a in obj.project.all()])


class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'host', 'key')
    search_fields = ['name']


class VoiceAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'project', 'contact', 'created_by', 'created_on')
    search_fields = ['project', 'contact']


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'show_groups', 'show_flows', 'lead', 'active', 'created_on')
    search_fields = ['name', 'group', 'lead']

    def show_groups(self, obj):
        return "\n".join([a.name for a in obj.group.all()])

    def show_flows(self, obj):
        return "\n".join([flow.name for flow in obj.flows.all()])


class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'language', 'urns', 'groups', 'blocked', 'stopped',
                    'created_on', 'modified_on', 'created_at')
    list_filter = ('created_on', 'modified_on', 'created_at', 'stopped', 'language')
    search_fields = ['name', 'urns', 'groups']


class MessageAdmin(admin.ModelAdmin):
    list_display = ('contact', 'urn', 'direction', 'type', 'status',
                    'visibility', 'text', 'labels', 'created_on', 'sent_on', 'modified_on', 'created_at', 'modified_at')
    list_filter = ('created_on', 'modified_on', 'created_at', 'status', 'type', 'direction')
    search_fields = ['urn', 'text', 'status']


class FlowAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'uuid', 'name', 'active_runs', 'complete_runs', 'interrupted_runs', 'expired_runs', 'created_on',
        'created_at', 'modified_at')
    search_fields = ['name']


class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'count',  'created_at', 'modified_at')
    search_fields = ['name']


class RunAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'run_id', 'flow', 'contact', 'responded', 'values', 'exit_type', 'exited_on', 'created_on', 'modified_on',
        'created_at', 'modified_at')
    list_filter = ('created_on', 'modified_on', 'created_at', 'responded', 'exit_type')
    search_fields = ['run_id', 'contact', 'flow']


class ValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'value_name', 'value', 'category', 'node', 'time', 'run_id',  'created_at', 'modified_at')
    search_fields = ['value', 'value_name']


admin.site.register(Project, ProjectAdmin)
admin.site.register(Voice, VoiceAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Workspace, WorkspaceAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Email, EmailAdmin)
admin.site.register(Run, RunAdmin)
admin.site.register(Flow, FlowAdmin)
admin.site.register(Campaign)
admin.site.register(CampaignEvent)
admin.site.register(Value, ValueAdmin)
