# noinspection PyUnresolvedReferences
from django.conf.urls import url, include
# noinspection PyUnresolvedReferences,PyUnresolvedReferences
from django_pdfkit import PDFView
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    # url(r'^login/$', auth_views.login, name='login', kwargs={'redirect_authenticated_user': True,
    #                                                          'template_name': 'userprofile/login.html',
    #                                                          'authentication_form': EmailAuthenticationForm,
    #                                                          'redirect_field_name': 'post',
    #                                                          }),
    url(r'^$', dashboard, name='dashboard'),
    url(r'^home/$', dashboard_nav, name='dashboard-nav'),
    url(r'^report/view-1/(?P<project_id>[\-\w]+)/$', report_template_one, name='template_one'),
    url(r'^report/email/csv/(?P<project_id>[\-\w]+)/$', send_csv_attachment_email, name='email-csv'),
    url(r'^report/csv/(?P<project_id>[\-\w]+)/$', export_to_csv, name='csv'),
    url(r'^report/csv/messages/(?P<project_id>[\-\w]+)/$', export_to_csv_all_messages, name='csv-messages'),
    url(r'^report/view-1/(?P<project_id>[\-\w]+)/groups/$', view_all_project_groups, name='all-project-groups'),
    url(r'^report/view-1/(?P<project_id>[\-\w]+)/contacts/$', view_all_project_contacts,
        name='all-project-contacts'),
    url(r'^report/view-1/(?P<project_id>[\-\w]+)/weekly-contacts/$', view_all_project_weekly_contacts,
        name='all-project-weekly-contacts'),
    url(r'^report/view-1/(?P<project_id>[\-\w]+)/weekly-hanging-messages/$', view_all_project_weekly_hanging_messages,
        name='all-project-weekly-hanging-messages'),
    url(r'^report/view-1/(?P<project_id>[\-\w]+)/weekly-failed-messages/$', view_all_project_weekly_failed_messages,
        name='all-project-weekly-failed-messages'),
    url(r'^report/view-1/(?P<project_id>[\-\w]+)/weekly-voice-interactions/$', view_all_project_weekly_voice_interactions,
        name='all-project-weekly-voice-interactions'),
    url(r'^my-pdf/$', PDFView.as_view(template_name='report/my-pdf.html'), name='my-pdf'),
    url(r'^pdf/$', generate_pdf_weekly_report, name='view_pdf'),
    url(r'^emails/(?P<project_id>[\-\w]+)/$', send_report_email, name='email'),
]
