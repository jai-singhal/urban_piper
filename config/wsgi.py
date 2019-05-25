"""
WSGI config for urban_piper project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import environ
from django.core.wsgi import get_wsgi_application


os.environ['AMPQ_URL' ] = "amqp://bcuvozzm:Suw5U981uKc7kLVtg4TOopfqlfT87VLS@spider.rmq.cloudamqp.com/bcuvozzm"
os.environ['AMPQ_HOSTNAME' ] = "spider.rmq.cloudamqp.com"
os.environ['AMPQ_PASSWORD' ] = "Suw5U981uKc7kLVtg4TOopfqlfT87VLS"
os.environ['AMPQ_USER' ] = "bcuvozzm:bcuvozzm"
os.environ['AMPQ_PORT' ] = "1883"

os.environ['POSTGRES_HOST' ] = "localhost"
os.environ['POSTGRES_PORT' ] = "5432"
os.environ['POSTGRES_DB' ] = "urban_piper"
os.environ['POSTGRES_USER' ] = "jai"
os.environ['POSTGRES_PASSWORD' ] = "root@123"

os.environ['DJANGO_SECRET_KEY' ] = "wCoBfAkvv8yxbATb123403T8T1K0ystL10Zg4R20iQ0KmvJlyabCjR6i8lAanUj"
os.environ['DJANGO_SETTINGS_MODULE' ] = "config.settings.production"



env = environ.Env()
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DJANGO_SETTINGS_MODULE'] = env(
    "DJANGO_SETTINGS_MODULE",
    default="config.settings.production",
)

application = get_wsgi_application()

