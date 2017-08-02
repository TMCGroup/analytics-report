from django.contrib import admin
from .models import Contact, Group, Run, Flow, Message, Workspace, Project, CampaignEvent, Campaign, Voice, Email


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
    list_display = ('id', 'name', 'show_groups', 'lead', 'active', 'created_on')
    search_fields = ['name', 'group', 'lead']

    def show_groups(self, obj):
        return "\n".join([a.name for a in obj.group.all()])


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'urns', 'groups', 'blocked', 'stopped',
                    'created_on', 'modified_on')
    list_filter = ('created_on', 'modified_on')
    search_fields = ['name', 'urns', 'groups']


class MessageAdmin(admin.ModelAdmin):
    list_display = ('contact', 'urn', 'direction', 'type', 'status',
                    'visibility', 'text', 'labels', 'created_on', 'sent_on', 'modified_on')
    list_filter = ('created_on', 'modified_on')
    search_fields = ['urn', 'text']


class FlowAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'uuid', 'name', 'active_runs', 'complete_runs', 'interrupted_runs', 'expired_runs', 'created_on')
    search_fields = ['name']


class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'count')
    search_fields = ['name']


class RunAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'run_id', 'flow', 'contact', 'responded', 'exit_type', 'exited_on', 'created_on', 'modified_on')
    search_fields = ['run_id', 'contact', 'flow']


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
