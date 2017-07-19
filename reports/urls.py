from django.conf.urls import url, include
import views as qc_views
from django_pdfkit import PDFView

urlpatterns = [
    url(r'^data/$', qc_views.getdatatest),
    url(r'^getget/$', qc_views.getget),
    url(r'^home/$', qc_views.dashboard, name='dashboard'),
    url(r'^project/$', qc_views.project_groups_detail, name='project-groups'),
    url(r'^report/version/one/(?P<project_id>[\-\w]+)/$', qc_views.report_template_one, name='template_one')

    # url(r'^$', qc_views.index),
    # url(r'^test_pdf_found/$', qc_views.html_to_pdf_view),
    # url(r'^sms_maama_weekly/$', qc_views.sms_maama_weekly),
    # url(r'^sms_maama_weekly_pdf/$', qc_views.print_report),
    # url(r'^sms_maama_weekly_pdf_2/$', qc_views.generate_pdf),
    # url(r'^sms_maama_weekly_pdf_3/$', qc_views.pdf_view),
    # url(r'^failed_messages/$', qc_views.daily_messages_failed),
    # url(r'^pdf/$', qc_views.MyPDFView.as_view()),
    # url(r'^test_pdf/$', qc_views.TestMyPDFView.as_view()),
    # url(r'^my-pdf/$', PDFView.as_view(template_name='my-pdf.html'), name='my-pdf'),
]
