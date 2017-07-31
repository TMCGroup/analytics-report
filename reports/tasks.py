from celery.schedules import crontab
from celery.task import periodic_task
from celery.utils.log import get_task_logger
from celery import shared_task
from .models import Group, Email, Message, RapidproKey, Run, Project


@shared_task
def get_rapidpro_data():
    RapidproKey.get_rapidpro_data()
    return


@shared_task
def organise_data():
    Message.assign_foreignkey()
    Run.assign_foreignkey()
    return


@shared_task
def get_hiwa_data():
    Project.get_project_voice_data()
    return


@shared_task
def send_emails():
    Email.email_report()
    return

