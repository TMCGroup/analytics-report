# Analytics Report
Analytics Report is a TMCG Project used to get SMS and Voice Platform data into a local database automatically
for purposes of reporting.

## Features
* Getting SMS Platform Data
* Getting Voice Platform Data
* Generating pdf and csv reports
* Sending weekly emails to project registered project leads

## Prerequisites

* Install requirements from requirements files.

* Make sure you have rabbitmq-server installed globally.

  * worker: "celery worker -A analyticreports --loglevel=INFO" run the worker from the root directory of the project.
	
  * scheduler: "celery -A analyticreports beat -l info -S django" run the scheduler from the root directory of the project.
	
  [For more info on celery tasks]
  (http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html(more about celery))
  
## Usage

* Create superuser and login to django admin
* Add Workspaces.
* Add Intervals and Crontabs for when periodic tasks should run.
* Add Periodic tasks getting the data.
* Add Projects(groups for which to generate excel/pdf/emails). This can be done after getting the group data from
rapidpro.
* Add Periodic tasks for generating excel/pdf/email.
* Add Emails.


