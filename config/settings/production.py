from .base import *  # noqa
from .base import env
from .base import APPS_DIR
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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {  
            'class': 'logging.FileHandler',
            'filename': os.path.normpath(os.path.join(APPS_DIR, '../django.log')),  
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            # 'handlers': ['console'],  
            'handlers': [ 'file'],  
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'), 
        },
    },
}

# Your stuff...
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["whitenoise"]
MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware']
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
SERVE_MEDIA_FILES = True
