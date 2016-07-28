# Initial requirements: #
* python 3
* postgres
* sudo apt-get install zlib1g-dev libtiff5-dev libjpeg8-dev libfreetype6-dev liblcms2-dev libwebp-dev

# Postgres setup steps(Ubuntu): #
* apt-get install libpq-dev python-dev
* sudo apt-get install postgresql postgresql-contrib

# Numpy installation for XIRR calculations. (Will take long time to install)
* sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran
* sudo apt-get install python-scipy


## Creating db and user ##
* sudo su - postgres
* createdb finaskus
* createuser finaskus --pwprompt (Please add "finaskus" as password)

## Setup commands: ##
* Installing dependencies: pip install -r requirements.txt
* Check your installation by running `from scipy import optimize` in python shell
* sudo su postgres -c "psql finaskus -c 'CREATE EXTENSION hstore;'"
* Running db migrations: python manage.py migrate
* Running server: python manage.py runserver

## Application setup: ##
* Run `python manage.py shell < webapp/fixtures/database.py`
* Run `python manage.py loaddata  webapp/fixtures/questions.json webapp/fixtures/options.json
webapp/fixtures/pincode_modified.json webapp/fixtures/ifsc_codes.json`
* The above commands will load the static data like questions, options, pincode and ifsc details.
* Follow instructions in funds_all_datpoints.py for setting up fresh funds or new funds.

## Environment keys and cron setup
* Inside the .bashrc. Please add the environment variables that needs to be set.
* Using the `python manage.py crontab add` command add the crons
* You will notice some line like this added `55 23 * * *  /home/ubuntu/projects/finaskus/finaskus-env/bin/python /home/ubuntu/projects/finaskus/backend-finaskus/manage.py crontab run 2ec9049278dc900585cf6a3cc02b41c3 #
 django-cronjobs for webapp` since we are using environment variable via bashrc we need to modify all of them and convert it too `55 23 * * *  bash -c 'source ~/.bashrc && /home/ubuntu/projects/finaskus/finaskus-env/bin/python /home/ubuntu/projects/finaskus/backend-finaskus/manage.py crontab run 2ec9049278dc900585cf6a3cc02b41c3' # django-cronjobs for webapp`


## Run test case ##
* You might need to elevate the user like this from psql shell before running the test `ALTER USER finaskus WITH SUPERUSER;`
* For Core API : `python manage.py test webapp/apps/core/`

## Sever setup
* Apart from all the above step you will have to install `pip install -r requirements_server.txt`
* Refer to `http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/` to setup gunicorn and ngnix
* After doing ngnix settings to route static file via ngnix itself run `python manage.py collectstatic`


## Server updates process
*  Log in to AWS
*  'cd ~/projects/finaskus'
*  'source finaskus-env/bin/activate'
*  cd backend-finaskus
* `sudo git pull origin <branch_name>` (ex master is the branch that needs to be pulled)
*  If any changes are done in static files(images & CSS( anything in static folder)) run `python manage.py collectstatic`
* `ps -ef | grep gunicorn` will list down the workers with their pids ( find gunicorn process & kill them)
* `sudo kill -9 <all the pids space seperated>` This will kill all the gunicorn process with that pid
*  ALTERNATELY it can be killed by `pkill -9 gunicorn` if we are sure gunicorn is only running our project alone
* from the location `/projects/finaskus/backend-finaskus` on current server run `nohup ./../finaskus-env/bin/gunicorn_start.sh &` to run the server again