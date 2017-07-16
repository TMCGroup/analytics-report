from django.contrib import admin
from .models import Contact, Group, Run, Flow, Message, RapidproKey, Project


# class EmailAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'address', 'project')
#     search_fields = ['name']


class RapidprokeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'workspace', 'host', 'key')
    search_fields = ['workspace']


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'show_groups', 'lead', 'active', 'created_on')
    search_fields = ['name', 'group', 'lead']

    def show_groups(self, obj):
        return "\n".join([a.name for a in obj.group.all()])


class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'language', 'urns', 'groups', 'blocked', 'stopped',
                    'created_on', 'modified_on')
    list_filter = ('created_on', 'modified_on')
    search_fields = ['name', 'urns', 'groups']


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'msg_id', 'contact', 'urn', 'broadcast', 'channel', 'direction', 'type', 'status',
                    'visibility', 'text', 'labels', 'created_on', 'sent_on', 'modified_on')
    list_filter = ('created_on', 'modified_on')
    search_fields = ['urn', 'text']


class FlowAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'active_runs', 'complete_runs', 'interrupted_runs', 'expired_runs', 'created_on')
    search_fields = ['name']


class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'count')
    search_fields = ['name']


class RunAdmin(admin.ModelAdmin):
    list_display = ('id', 'run_id', 'flow', 'contact', 'responded', 'exit_type', 'exited_on', 'created_on', 'modified_on')
    search_fields = ['run_id', 'contact', 'flow']


# class StepAdmin(admin.ModelAdmin):
#     list_display = ('id', 'node', 'time', 'run_id')
#     search_fields = ['node']
#
#
# class ValueAdmin(admin.ModelAdmin):
#     list_display = ('id', 'value', 'run_id')
#     search_fields = ['value']


admin.site.register(Project, ProjectAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(RapidproKey, RapidprokeyAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Group, GroupAdmin)
# admin.site.register(Email, EmailAdmin)
admin.site.register(Run, RunAdmin)
admin.site.register(Flow, FlowAdmin)
# admin.site.register(Step, StepAdmin)
# admin.site.register(Value, ValueAdmin)
