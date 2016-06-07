# Initial requirements: #
* python 3
* postgres
* sudo apt-get install zlib1g-dev libtiff5-dev libjpeg8-dev libfreetype6-dev liblcms2-dev libwebp-dev

# Postgres setup steps(Ubuntu): #
* apt-get install libpq-dev python-dev
* sudo apt-get install postgresql postgresql-contrib

# Numpy installation for XIRR calculations. (Will take log time to install)
* sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran
* sudo apt-get install python-scipy

## Creating db and user ##
* sudo su - postgres
* createdb finaskus
* createuser finaskus --pwprompt (Please add "finaskus" as password)

## Setup commands: ##
* Installing dependencies: pip install -r requirements.txt
* sudo su postgres -c "psql finaskus -c 'CREATE EXTENSION hstore;'"
* Running db migrations: python manage.py migrate
* Running server: python manage.py runserver

## Application setup: ##
* Run `python manage.py shell < webapp/fixtures/database.py`
* Run `python manage.py loaddata  webapp/fixtures/questions.json webapp/fixtures/options.json webapp/fixtures/pincode.json webapp/fixtures/funds.json`
* Run `python manage.py shell < webapp/fixtures/funds_all_datapoints.py`

## Run test case ##
* You might need to elevate the user like this from psql shell before running the test `ALTER USER finaskus WITH SUPERUSER;`
* For Core API : `python manage.py test webapp/apps/core/`
