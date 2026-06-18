import os

from .base import *

DEBUG = False

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "production-locmem",
    }
}