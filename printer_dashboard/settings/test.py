"""
With these settings, tests run faster.
"""

from .base import *  # noqa

# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

FRONTEND_URL = "https://printer_dashboard.com"
