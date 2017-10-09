# Analytics Report
Analytics Report is a TMCG Project used to get SMS and Voice Platform data into a local database
for purposes of reporting.

## Features
* Getting SMS Platform Data
* Getting Voice Platform Data
* Generating pdf and csv reports
* Sending weekly emails to registered project leads


## Prerequisite
* Make sure you have rabbitmq-server installed globally.


## Installation
```
#clone the project.
git clone (project-link)

#Install requirements.
pip install requirements.pip

#create .env file in the project's root directory
This file should contain all variables provided in settings.py. Refer to the env.sample file in the project root
directory to aid you create the .env file.

#Migrate migrations
python manage.py migrate

#Follow *Usage* steps provided in the section below this one.
steps (1) to (3)

#Run django server in one terminal
python manage.py runserver

#Run the worker in another terminal
 celery worker -A analyticreports --loglevel=INFO
	
#Run the scheduler in another terminal
celery -A analyticreports beat -l info -S django

#Follow *Usage* steps provided in the section below this one.
step (4) to (5)

 ```
 [For more info on periodic tasks](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html)


## Usage

* (1) Create superuser by running`python manage.py createsuperuser` and Visit http://127.0.0.1:8000/admin then
login using your created superuser credentials.
* (2) Add Workspaces(available under reports in the side menu and control panel), this should be straight forward when
logged in django admin.
* (3) Add Periodic tasks (available under django celery beat in the side menu and control panel) for get_workspace_data,
 get_hiwa_data and send_emails. Use Intervals or Crontabs accordingly.
* (4) Add Project (select groups and flows for respective project whose report is to be generated). This should be done
after fetching. Also register the Emails that will be receiving the reports under Emails in django admin.
data from RapidPro workspaces.
* (5) Visit http://127.0.0.1:8000/home, this might take awhile to initially load depending on available data. Select any
 of the other links provided in the side bar to visit particular project results.
* (6) Modify Projects and Emails in django admin as required whenever.


