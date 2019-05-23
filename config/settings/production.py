from .base import *  # noqa
from .base import env

DEBUG = False

SECRET_KEY = env("DJANGO_SECRET_KEY")
# ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["https://urbanpiper.com"])
ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': env("POSTGRES_DB"),
        'HOST': env("POSTGRES_HOST"),
        'PORT': '5432',                    
        'USER': env("POSTGRES_USER"),
        'PASSWORD': env("POSTGRES_PASSWORD"),                             
    }
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

INSTALLED_APPS += ["gunicorn"]

# LOGGING
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console", "mail_admins"],
            "propagate": True,
        },
    },
}

# Your stuff...
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["whitenoise"]
MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware']
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
SERVE_MEDIA_FILES = True