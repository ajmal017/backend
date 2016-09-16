import os

BASE_URL="http://10.0.2.15:8000"
SITE_BASE_URL="http://10.97.11.86"

CVL_POSCODE="5100108537"
CVL_PASSWORD="FIN@123"
CVL_PASSKEY="FINASKUSTEST"
CVL_USERID="VIEWONLY"
CVL_PASSWORD_URI="https://www.cvlkra.com/PanInquiry.asmx/GetPassword"
CVL_PANCARD_URI="https://www.cvlkra.com/panInquiry.asmx/GetPanStatus"
BILLDESK_SECRET_KEY="2KxU2EvL4enK"
MGAGE_USERNAME="FINASKUST"
MGAGE_PASSWORD="C2P3B@n@"
MGAGE_FROM_NUMBER=918050248326
BASE_URL="http://localhost:8000"
SITE_BASE_URL="www.finaskus.com"
SITE_API_BASE_URL = "api.finaskus.com"



EMAIL_BACKEND='django_smtp_ssl.SSLEmailBackend'
EMAIL_HOST='email-smtp.us-west-2.amazonaws.com'
EMAIL_PORT=465
DEFAULT_FROM_EMAIL = 'Finaskus Support<askus@finaskus.com>'
DEFAULT_TO_EMAIL = "jineshpaul@finaskus.com"
EMAIL_HOST_USER=os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_HOST_PASSWORD')

MORNING_STAR_UNIVERSE_ID="wlwhm2lfm9boisdt"
MORNING_STAR_ACCESS_CODE="ah0y3b7c6zy4yvmi22rh5d6felljtam0"
MORNING_STAR_UNIVERSE_ID_EQUITY='x28l3ltc7hrsrrdq'
MORNING_STAR_UNIVERSE_ID_DEBT='f351pmwnr55evt0j'
MORNING_STAR_UNIVERSE_ID_INDICES='ttr83nzvyxn4lrvs'

EMAIL_HOST_USER='AKIAILOEFIX3NX3REUGA'
EMAIL_HOST_PASSWORD='AqM9b5AHqFuNbesfNJrVvQHx2gDj4DUV2fwxyCbJgITD'
DATABASE_NAME='finaskus'
DATABASE_USER='finaskus'
DATABASE_PASSWORD='finaskus'
DATABASE_HOST='localhost'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': '',
    }
}


DEBUG = True
ALLOWED_HOSTS = ['*']
TEMPLATE_DEBUG = True
USING_S3=False
