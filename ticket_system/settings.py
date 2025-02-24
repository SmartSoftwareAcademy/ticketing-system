"""
Django settings for ticket_system project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
#from ticketapp.models import *
from django.core.management.utils import get_random_secret_key
from pathlib import Path
import os
import sys
import dj_database_url
from .juzmin import JAZZMIN_SETTINGS


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
#email_settings = OutgoinEmailSettings.objects.all()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-u9z&&4a0q%p^%+*^nnfmm(k6oqe1k%1i!p7@_k2kxv^8inq&i&'
#SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())
# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True
DEBUG = os.getenv("DEBUG", "True") == "True"

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "True") == "True"
#ALLOWED_HOSTS = ['support.tdbsoft.co.ke', 'localhost', '127.0.0.1']
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS",
                          "127.0.0.1,localhost").split(",")
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'tinymce',
    #custom apps
    'accounts',
    'resource_center',
    'ticketapp',
]

# This scheduler config will:
# - Store jobs in the project database
# - Execute jobs in threads inside the application process
# SCHEDULER_CONFIG = {
#     "apscheduler.jobstores.default": {
#         "class": "django_apscheduler.jobstores:DjangoJobStore"
#     },
#     'apscheduler.executors.processpool': {
#         "type": "threadpool"
#     },
# }
SCHEDULER_AUTOSTART = True

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

ROOT_URLCONF = 'ticket_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ticketapp.context_processors.get_site_setup',
            ],
        },
    },
]

WSGI_APPLICATION = 'ticket_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'helpdesk',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'root',
        'PORT': 3306,
    }
}
# if DEVELOPMENT_MODE is True:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'helpdesk.sqlite3',
#         }
#     }
# elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
#     if os.getenv("DATABASE_URL", None) is None:
#         raise Exception("DATABASE_URL environment variable not defined")
#     DATABASES = {
#         "default": dj_database_url.parse(os.environ.get("DATABASE_URL")),
#     }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    'http://localhost:8080',
    'http://localhost:8081',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_INSPECTORS': [
        'rest_framework.filters.DjangoFilterInspector',
    ],
    'SEARCH_PARAM': 'q',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12
}
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
MEDIA_URL = '/media/'  # This is just for url i.e https://l.me/media/l.jpg
# This is the folder the image will be uploaded
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# .format(email_settings.email_backed)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ''  # email_settings.email_host  # 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = ''  # email_settings.email_port  # 587
EMAIL_HOST_USER = ''  # email_settings.support_reply_email  # 'titusowuor30@gmail.com'
EMAIL_HOST_PASSWORD = ''  # email_settings.email_password  # 'xdofqrtncuimlewm'

TINYMCE_JS_ROOT = os.path.join('static')
TINYMCE_DEFAULT_CONFIG = {

    'height': 540,
    'width': 920,
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'silver',
    'plugins': '''
   textcolor save link image media preview codesample contextmenu
   table code lists fullscreen insertdatetime nonbreaking
   contextmenu directionality searchreplace wordcount visualblocks
   visualchars code fullscreen autolink lists charmap print hr
   anchor pagebreak help
   ''',
    'toolbar1': '''
   fullscreen preview bold italic underline | fontselect,
   fontsizeselect | forecolor backcolor | alignleft alignright |
   aligncenter alignjustify | indent outdent | bullist numlist table |
   | link image media | codesample |
   ''',
    'toolbar2': '''
   visualblocks visualchars |
   charmap hr pagebreak nonbreaking anchor | code |
   ''',
    'contextmenu': 'formats | link image',
    'menubar': True,
    'statusbar': True,
}
#TINYMCE_SPELLCHECKER = True
TINYMCE_COMPRESSOR = False
TINYMCE_JS_URL = os.path.join('tinymce', "tinymce.min.js")
JAZZMIN_SETTINGS = JAZZMIN_SETTINGS
# TINYMCE_EXTRA_MEDIA = {
#     'css': {
#         'all': [
#             ...
#         ],
#     },
#     'js': [
#         ...
#     ],
# }
