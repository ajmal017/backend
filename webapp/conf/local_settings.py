import os

BASE_URL="http://localhost:8000"
SITE_BASE_URL="www.finaskus.com"

CVL_POSCODE=os.environ.get('CVL_POSCODE')
CVL_PASSWORD=os.environ.get('CVL_PASSWORD')
CVL_PASSKEY=os.environ.get('CVL_PASSKEY')
CVL_USERID=os.environ.get('CVL_USERID')
CVL_PASSWORD_URI=os.environ.get('CVL_PASSWORD_URI')
CVL_PANCARD_URI=os.environ.get('CVL_PANCARD_URI')
BILLDESK_SECRET_KEY=os.environ.get('BILLDESK_SECRET_KEY')

EMAIL_BACKEND='django_smtp_ssl.SSLEmailBackend'
EMAIL_HOST='email-smtp.us-west-2.amazonaws.com'
EMAIL_PORT=465
DEFAULT_FROM_EMAIL = 'Finaskus Support<askus@finaskus.com>'
DEFAULT_TO_EMAIL = "appadmin@finaskus.com"
EMAIL_HOST_USER=os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_HOST_PASSWORD')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': '5432',
    }
}


DEBUG = False
ALLOWED_HOSTS = ['*']
TEMPLATE_DEBUG = False

MGAGE_USERNAME = os.environ.get('MGAGE_USERNAME')
MGAGE_PASSWORD = os.environ.get('MGAGE_PASSWORD')
MGAGE_FROM_NUMBER = int(os.environ.get('MGAGE_FROM_NUMBER'))

MORNING_STAR_UNIVERSE_ID = os.environ.get('MORNING_STAR_UNIVERSE_ID')
MORNING_STAR_ACCESS_CODE = os.environ.get('MORNING_STAR_ACCESS_CODE')
MORNING_STAR_UNIVERSE_ID_EQUITY = os.environ.get('MORNING_STAR_UNIVERSE_ID_EQUITY')
MORNING_STAR_UNIVERSE_ID_DEBT = os.environ.get('MORNING_STAR_UNIVERSE_ID_DEBT')
MORNING_STAR_UNIVERSE_ID_INDICES = os.environ.get('MORNING_STAR_UNIVERSE_ID_INDICES')
