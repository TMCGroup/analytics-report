# analyticreports
Analyticreports is a project to get rapidpro data into a local database automatically. This data can be reported on in different forms(pdf/excel).
The data can also be manipulated with custom methods.

Prerequisites
-Install requirements from requirements files.
-Make sure you have rabbitmq-server installed globally.
  -worker: "celery worker -A analyticreports --loglevel=INFO" run the worker from the root directory of the project.
  -scheduler: "celery -A analyticreports beat -l info -S django" run the scheduler from the root directory of the project.
  -http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html(more about celery)
  
Usage/procedure
-Enter Rapidpro host & key in database.
-Create intervals and crontabs(in the database). When periodic tasks should run.
-Create periodic tasks(in the database) for getting rapidpro data.
-Create projects(groups for which to generate excel/pdf/emails). This can be done after getting the group data from rapidpro.
-Create periodic tasks for generating excel/pdf/email.
-It can generate excel and pdf files of this data.
-It can also email these excel and pdf files to specific email(also have to be stored in the database).

