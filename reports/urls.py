from django.conf.urls import url, include
from .views import *


urlpatterns = [
    url(r'^home/$', dashboard, name='dashboard'),
    url(r'^report/email/csv/(?P<project_id>[\-\w]+)/$', send_csv_attachment_email, name='email-csv'),
    url(r'^report/csv/(?P<project_id>[\-\w]+)/$', export_to_csv, name='csv'),
    url(r'^project/$', project_groups_detail, name='project-groups'),
    url(r'^report/version/one/(?P<project_id>[\-\w]+)/$', report_template_one, name='template_one'),
    url(r'^data/$', getdatatest),
    url(r'^getget/$', getget),
]
