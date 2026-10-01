"""Test settings for the project."""

from .local import *

DEBUG = False

SECURE_SSL_REDIRECT = False
WHITENOISE_MANIFEST_STRICT = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
