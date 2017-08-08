# Analytics Report
Analytics Report is a TMCG Project used to get SMS and Voice Platform data into a local database
for purposes of reporting.

## Features
* Getting SMS Platform Data
* Getting Voice Platform Data
* Generating pdf and csv reports
* Sending weekly emails to project registered project leads


## Prerequisite
* Make sure you have rabbitmq-server installed globally.

## Installation
```
#clone the project.
git clone (project-link)

#Install requirements.
pip install requirements.pip

#Run django server
python manage.py runserver

#Run the worker.
 celery worker -A analyticreports --loglevel=INFO
	
#Run the scheduler.
celery -A analyticreports beat -l info -S django

 ```
 [For more info on periodic tasks](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html)

## Usage

* Create superuser `python manage.py createsuperuser` and login via django admin
* Add Workspaces.
* Add Intervals and Crontabs for when periodic tasks should run.
* Add Periodic tasks for getting the data.
* Add Projects(groups for which to generate excel/pdf/emails). This can be done after getting the group data from
rapidpro.
* Add Periodic tasks for generating excel/pdf/email.
* Add Emails.
* Visit http://127.0.0.1:8000/home.


