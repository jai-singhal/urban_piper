from .base import *  # noqa
from .base import env
print("Local settings")

# GENERAL
DEBUG = True

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="DobIZIyXgDHlPoneKndwWCmfdbnT7I2LOhR9Tybpo0TFGEdgN9KuJaD6aI8FOKCM",
)

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

# CACHES

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}
INSTALLED_APPS += [
    "debug_toolbar"
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]