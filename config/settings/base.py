import os


import environ

ROOT_DIR = (
    environ.Path(__file__) - 3
)  # (urban_piper/config/settings/base.py - 3 = urban_piper/)
APPS_DIR = ROOT_DIR.path("urban_piper")
env = environ.Env()




BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '6iz%$w^)t=r(e)g=q#$5v0f*2tnhtj$k6&$225$=zn8x=_k@vr'
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

INSTALLED_APPS += [
    "channels",
    "crispy_forms",
    'django_celery_results',

    "urban_piper.core",
    "urban_piper.users",

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(APPS_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ASGI APPLICATION
ASGI_APPLICATION = "config.routing.application"

# REDIS SETTINGS
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

AUTH_USER_MODEL = "users.User" 

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

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

# AUTHENTICATION_BACKENDS = ["urban_piper.users.backend.AuthenticationBackend"]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

CRISPY_TEMPLATE_PACK = 'bootstrap4'

STATIC_URL = '/static/'
STATIC_ROOT = str(ROOT_DIR("staticfiles"))
STATICFILES_DIRS = [str(APPS_DIR.path("static"))]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# MEDIA_ROOT = str(ROOT_DIR("mediafiles"))
MEDIA_URL = "/media/"

import pika
PIKA_CONNECTION = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# PIKA_CONNECTION.add_timeout(1)
PIKA_CHANNEL = PIKA_CONNECTION.channel()
PIKA_CHANNEL.queue_declare(queue='high')
PIKA_CHANNEL.queue_declare(queue='medium')
PIKA_CHANNEL.queue_declare(queue='low')
PIKA_CHANNEL.basic_qos(prefetch_count=1)