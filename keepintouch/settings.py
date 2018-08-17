"""
Django settings for keepintouch project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import ast
import sys, traceback

import dj_database_url
from urllib.parse import urlparse


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY','')
#SECRET_KEY = os.environ["SECRET_KEY"]
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG =  ast.literal_eval(os.environ.get('DJANGO_DEBUG','True'))

DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL' : ''
}

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = (
    '0.0.0.0',
    '127.0.0.1',
)

KIT_IS_SAAS = ast.literal_eval(os.environ.get('KIT_IS_SAAS','False'))

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    #'django.contrib.sites',
    'core.apps.CoreConfig',
    'gomez.apps.GomezConfig',
    #'messaging',
    'messaging.apps.MessagingConfig',
    'reportng.apps.ReportngConfig',
    'kitcall',
    'randomslugfield',
    'crispy_forms',
    'crispy_forms_foundation',
    'django_tables2',
    'django_select2',
    'django_filters',
    'tinymce',
    'autofixture',
    'django_rq',
    'django_ajax',
    'sitegate',
    'import_export',
    'stronghold',
    'analytical',
    'country_dialcode',
    'cacheops',
    'password_reset',
    'cities_light',
    'django_nvd3',
    'watson',
    'django_prices',
    'django_activeurl',
    'django_bootstrap_breadcrumbs',
    'rest_framework',
    
]

if DEBUG == True:
    INSTALLED_APPS+=['debug_toolbar']

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'stronghold.middleware.LoginRequiredMiddleware',
    'core.middleware.TimeZoneMiddleware',
    'core.middleware.UserValidatedMiddleware',
    'core.middleware.SubscriptionExpiredMiddleware',
]

FERNET_KEYS = [
    os.environ.get('FERNET_KEY_1')
]

ROOT_URLCONF = 'keepintouch.urls'

AUTHENTICATION_BACKENDS = [
     'django.contrib.auth.backends.ModelBackend',                 
                           ]

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

TEMPLATES[0]['OPTIONS']['context_processors'].append("messaging.context_processors.issue_form_processor")
TEMPLATES[0]['OPTIONS']['context_processors'].append("messaging.context_processors.total_failed_messages_count")


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}


CRISPY_ALLOWED_TEMPLATE_PACKS = ('bootstrap', 'uni_form', 'bootstrap3', 'foundation-5')

CRISPY_TEMPLATE_PACK = 'foundation-5'

SELECT2_JS = 'js/select2.js'
SELECT2_CSS = 'css/select2.css'

ACTIVE_URL_KWARGS = {
    'css_class': 'active',
    'parent_tag': 'li',
    'menu': 'yes'
}

BREADCRUMBS_TEMPLATE = "core/breadcrumb/foundation.html"

'''
FILEBROWSER_EXTENSIONS = {
    'Image': ['.jpg','.jpeg','.gif','.png']
}

FILEBROWSER_SELECT_FORMATS = {
    'image': ['Image']
}
FILEBROWSER_VERSIONS_BASEDIR = '_versions'
'''

#TINYMCE_FILEBROWSER = True
TINYMCE_JS_URL = "js/tinymce/tinymce.min.js"
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table, spellchecker, paste, hr, searchreplace, legacyoutput, anchor, code, textcolor, colorpicker,\
                link, autolink, image, imagetools, fullscreen, fullpage",
    'toolbar': "forecolor, backcolor, fontselect, fontsizeselect, visualblocks, link, fullscreen",
    'theme': "modern",
    'min_height': 600,
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    #'file_browser_callback': 'DjangoFilebrowser'
}

WSGI_APPLICATION = 'keepintouch.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE' : 'django.db.backends.postgresql_psycopg2',
        'NAME' : 'kitdev',
        'USER' : 'postgres',
        'PASSWORD' : 'password',
        'HOST' : 'localhost'
    },
    'delivery_report': {
        'ENGINE' : 'django.db.backends.postgresql_psycopg2',
        'NAME' : 'kitmsgdr',
        'USER' : 'postgres',
        'PASSWORD' : 'password',
        'HOST' : 'localhost'
    }
}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

DATABASES['delivery_report'] = dj_database_url.parse("{}".format(os.environ.get('DR_DATABASE_URL',\
                            'postgres://postgres:password@localhost:5432/kitmsgdr')), conn_max_age=600)

DATABASE_ROUTERS = ['reportng.routers.DeliveryReportRouter']


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

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
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter' : 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter' : 'verbose',
        }
    },    
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False if DEBUG else True

GOOGLE_ANALYTICS_PROPERTY_ID = ''
GOOGLE_ANALYTICS_SITE_SPEED = True


PHONENUMBER_DEFAULT_REGION = 'NG'

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-UK'

TIME_ZONE = 'Africa/Lagos'

USE_I18N = True

USE_L10N = False

DATE_FORMAT = 'd/m/Y'

DATE_INPUT_FORMATS = [
    '%d-%m-%Y', '%d/%m/%Y', '%d/%m/%y',
    '%d %b %Y', '%d %b, %Y',
]

DATETIME_INPUT_FORMATS = [
    '%d-%m-%Y %H:%M',        # '2006-10-25 14:30'
]

USE_TZ = True

CRISPY_FAIL_SILENTLY = not DEBUG


# Fixtures directory
#FIXTURE_DIRS = (os.path.join(BASE_DIR, 'fixtures'),)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#MEDIA_URL = '/media/'

#MEDIA_ROOT = "C:/Users/Dayo/git2/keepintouch/media/"

#STATIC_ROOT = "C:/Users/Dayo/git2/keepintouch/static"

STATICFILES_DIRS = ( 
      os.path.join(BASE_DIR, 'static'),
)

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'


DEFAULT_CURRENCY = 'NGN'

MSG_WAIT_TIME = 300
MAX_MSG_RECIPIENT = 30
MIN_BALANCE_TRANSFERABLE = 5
COMPANYWIDE_CONTACTS = True
ALLOWED_CONTENT_TYPES = ['application/csv','text/csv', 'application/vnd.ms-excel']#, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
MAX_UPLOAD_FILE_SIZE = 2621440

RESET_SMS_DAY_TIME = [0,"09"] #weekday, sunday is 0. Time of Day

redis_url = os.environ.get('REDIS_URL', 'redis://192.168.56.102:6379')
RQ_QUEUES = {
    'default': {
        'URL' : redis_url,
        'DB': 0,
        'DEFAULT_TIMEOUT': 1000,
    },
    'sms': {
        'URL' : redis_url,
        'DB': 0,
        'DEFAULT_TIMEOUT': 1000,
    },
    'email': {
        'URL' : redis_url,
        'DB': 0,
        'DEFAULT_TIMEOUT': 1000,
    }
}

CACHEOPS_REDIS = "%s/0"%redis_url

CACHEOPS = {
    'auth.user': {'ops': 'get', 'timeout': 60*15},
    'auth.*': {'ops': ('fetch', 'get'), 'timeout': 60*60},
    'auth.permission': {'ops': 'all', 'timeout': 60*60},
    '*.*': {'ops': (), 'timeout': 60*60}
}


RQ_SHOW_ADMIN_LINK = True

LOGIN_URL = '/'

SITEGATE_SIGNUP_ENABLED = True
SITEGATE_SIGNUP_DISABLED_TEXT = ''

INFOBIP_USERNAME = os.environ.get('INFOBIP_USERNAME', '')
INFOBIP_PASSWORD = os.environ.get('INFOBIP_PASSWORD', '')

WEBHOOK_KEY = ''
WEBHOOK_BASE_URL = ''

GOOGAPI_KEY = os.environ.get('GOOGAPI_KEY','')

SERVER_EMAIL = 'system-notification@intouchng.com'
ADMINS = [('Dayo', 'dayo.ayeni@tekartng.com'), ('In.Touch', 'support@intouchng.com')]

DEFAULT_FROM_EMAIL = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_HOST = ''
EMAIL_PORT = 26


SUPPORT_EMAIL = {
        'smtp_server':'mail.intouchng.com',
        'from_user' : 'In.Touch Support',
        'smtp_port' : 26,
        'smtp_user' : '',
        'smtp_password' : '',
                 }


STRONGHOLD_PUBLIC_URLS = (
    r'^/admin.*?$',
    r'^/$',
    r'^/register/free-trial/$',
    r'^/account/password/recover.*?$',
    r'^/account/password/reset.*?$',
    r'^/reports/sms/delivery/infobip/$',
    r'^/reports/webhook/cdr/$',
    r'^/reports/email/event/sendgrid/$',
    r'/register/email-validate/.*?$',
)

INTOUCH_FS_GW = os.environ.get('INTOUCH_FS_GW','127.0.0.1')
INTOUCH_FS_GW_PWD = os.environ.get('INTOUCH_FS_GW','')
INTOUCH_TERM_GW = os.environ.get('INTOUCH_TERM_GW','')


FREE_TRIAL_FREE_CREDIT = 20
SYSTEM_KITUSER_ID = os.environ.get('SYSTEM_KITUSER_ID','30')
FREE_TRIAL_SERVICE_PLAN_ID = os.environ.get('FREE_TRIAL_SERVICE_PLAN_ID','2')
FREE_TRIAL_VALIDITY_PERIOD = 14
FREE_TRIAL_GROUP_PERMS_ID = os.environ.get('FREE_TRIAL_GROUP_PERMS_ID','4')

STANDARD_KITUSER_GROUP_PERMS_ID = os.environ.get('STANDARD_KITUSER_GROUP_PERMS_ID','3')

CITIES_LIGHT_CITY_SOURCES = ['http://download.geonames.org/export/dump/NG.zip']
CITIES_LIGHT_TRANSLATION_SOURCES = []

CITIES_LIGHT_TRANSLATION_LANGUAGES = ['en']
CITIES_LIGHT_INCLUDE_COUNTRIES = ['NG']
CITIES_LIGHT_INCLUDE_CITY_TYPES = ['ADM2']#['PPL', 'PPLA', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLC',\
                                    #'PPLF', 'PPLG', 'PPLL', 'PPLR', 'PPLS', 'STLMT',]

# GENERAL
# =======
# PREFIX_LIMIT_MIN & PREFIX_LIMIT_MAX are used to know
# how many digits are used to match against the dialcode prefix database
PREFIX_LIMIT_MIN = 1
PREFIX_LIMIT_MAX = 6

# If PN is lower than PN_MIN_DIGITS it will be considered as an extension
# If PN is longer than PN_MIN_DIGITS but lower than PN_MAX_DIGITS then
# The PN will be considered as local call and the LOCAL_DIALCODE will be added
LOCAL_DIALCODE = 234  # Set the Dialcode of your country (44 for UK, 1 for US)
PN_MIN_DIGITS = 6
PN_MAX_DIGITS = 9

# List of phonenumber prefix to ignore, this will be remove prior analysis
PREFIX_TO_IGNORE = "+,0,00,000,0000,00000,011,55555,99999"

# When the PN len is less or equal to INTERNAL_CALL, the call will be considered
# as a internal call, for example when dialed number is 41200 and INTERNAL_CALL=5
INTERNAL_CALL = 5


if os.environ.get('ENV_VAR') == 'production':
    try:
        from .aws_settings import *
    except ImportError:
        sys.stderr.write("Can't find 'aws_settings.py'")
        traceback.print_exc()