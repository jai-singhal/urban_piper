import os
import environ

ROOT_DIR = (
    environ.Path(__file__) - 3
)  # (avyukt/config/settings/base.py - 3 = avyukt/)
APPS_DIR = ROOT_DIR.path("avyukt")
env = environ.Env()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="DobIZIyXgDHlPoneKndwWCmfdbnT7I2LOhR9Tybpo0TFGEdgN9KuJaD6aI8FOKCM",
)
DEBUG = True

ALLOWED_HOSTS = []

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    "channels",
    "crispy_forms",
]

LOCAL_APPS = [
    "avyukt.core",
    "avyukt.users",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


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

# WSGI_APPLICATION = 'config.wsgi.application'

# ASGI APPLICATION
ASGI_APPLICATION = "config.routing.application"

# REDIS SETTINGS
## redis backend
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('127.0.0.1', 6379)],
#         },
#     },
# }
# rabbitmq backend
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_rabbitmq.core.RabbitmqChannelLayer",
        "CONFIG": {
            # if having any amqp server url use that url
            "host": env("AMQP_URL", default = "amqp://guest:guest@localhost:5672")
            # "ssl_context": ... (optional)
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

# AUTHENTICATION_BACKENDS = ["avyukt.users.backend.AuthenticationBackend"]

LANGUAGE_CODE = 'en-us'
TIME_ZONE =  'Asia/Kolkata'
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


#ampq settings
AMQP_URL = env("AMQP_URL", default="localhost")