"""
Django settings for webapp project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v&$s@g3a7cafqcut=ua(9_%(6janl5q28eul#@*oj!0+)+7j0q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Installed apps

DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.postgres",
    # 'django_extensions'
]

THIRD_PARTY_APPS = [
    "rest_framework",
    'oauth2_provider',
    'django_crontab',
    'import_export',
    'django_smtp_ssl'
]

LOCAL_APPS = [
    "profiles",
    "core",
    "external_api",
    "payment"
]


INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'profiles.middleware.AutoLogout',
)


ROOT_URLCONF = 'webapp.urls'

WSGI_APPLICATION = 'webapp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'finaskus',
        'USER': 'finaskus',
        'PASSWORD': 'finaskus',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
        'PORT': '',  
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

 

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'statics')
#STATIC_ROOT = '/statics/'

STATICFILES_DIRS = (
   os.path.join(BASE_DIR, 'static'),
)

#if DEBUG: 
 #  STATIC_ROOT = os.path.join(BASE_DIR, '/statics')
#else:
 #  STATIC_ROOT = os.path.join(BASE_DIR, 'statics') 



STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'compressor.finders.CompressorFinder',
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                "django.core.context_processors.request",
            ],
            'debug': True
        },
    },
]


HOST = '127.0.0.1:8000'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },

    'handlers': {
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': 'error_log/debug.log',
        },
        'info_debug': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': 'error_log/info.log',
        },
        'warning_debug': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': 'error_log/warning.log',
        },
        'error_debug': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': 'error_log/error.log',
        },
        'critical_debug': {
            'level': 'CRITICAL',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': 'error_log/critical.log',
        },
        'monthly_debug': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': 'error_log/monthly.log',
        },
        'daily_debug': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': 'error_log/daily.log',
        },
        'mail_admins': {
            'level': 'INFO',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.monthly': {
            'handlers': ['monthly_debug', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.daily': {
            'handlers': ['daily_debug', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.debug': {
            'handlers': ['file_debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.info': {
            'handlers': ['info_debug', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.warning': {
            'handlers': ['warning_debug'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.error': {
            'handlers': ['error_debug'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.critical': {
            'handlers': ['critical_debug'],
            'level': 'CRITICAL',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        }
    },
}


SERVER_EMAIL = 'askus@finaskus.com'

ADMINS = (
    ('Finaskus', 'techops@finaskus.com')
)

'''REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}
'''

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope', 'groups': 'Access to your groups'},
    'ACCESS_TOKEN_EXPIRE_SECONDS': 86400  # TODO: revert to 1 week once refresh token is implemented
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    )
}

LOGIN_URL = '/login/'
DEFAULT_CHARSET = 'ISO-8859-1'
AUTH_USER_MODEL = 'profiles.User'
USE_HTTPS = True
ROTATE_IMAGE = False  # True means rotation of portrait size image to landscape is mandatory. False means does
# not rotate the portrait images.
ATTACH_IMAGE = False  # True means attaches images at appropriate pages instead of embedding them. False embeds.

# ====================================================================================================================
CLIENT_ID = "zTfCegJvxFQE1yxb2ga7sXHPwptm0im78dmFP6AD"
CLIENT_SECRET = "IecZLwFOrOmncFgBXBst38DmY5UJhioVcUSbZvYE19Esr9zOBMaW0HnstnzRXYmKZGCQoixgyhEfXKl5xx97rnqrUkWxX13oGgOmWi3qYMjWyFQKo5l3ydytkwMHiWNj"
BASE_URL = "http://localhost:8000"


CRONJOBS = [
    ('30 8 16 * *', 'webapp.cron.monthly_cron'),
    ('00 7 * * *', 'webapp.cron.daily_cron'),
    ('30 8 * * *', 'webapp.cron.daily_cron'),
    ('00 11 * * *', 'webapp.cron.daily_cron'),
    ('00 14 * * *', 'webapp.cron.daily_cron'),
    ('00 22 * * *', 'webapp.cron.daily_cron'),
    ('59 23 * * *', 'webapp.cron.daily_cron'),
    ('00 7 * * *', 'webapp.cron.daily_once_cron'),
]

START_DATE = None

# Handle session is not Json Serializable
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
AUTO_LOGOUT_DELAY = 60  # compulsory logout after 60 mins, whether or not the admin is interacting actively.
INACTIVE_LOGOUT_DELAY = 10  # admin inactive timeout, if admin has been inactive for more than 10 mins.

USING_S3 = False

try:
    from .local_settings import *
    # you can add SITE_BASE_URL = "localhost:8000" in a file called local_settings.py
except:
    # Ideally this should be the base url of the site since there is no domain name its like this
    SITE_BASE_URL = "www.finaskus.com"
    SITE_API_BASE_URL = "api.finaskus.com"

if os.environ.get('ENV_VAR') == 'prod':
    from .aws_settings import *
    

