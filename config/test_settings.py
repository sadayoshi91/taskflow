"""Test settings for the TaskFlow project.

This module keeps the normal development configuration focused on PostgreSQL
and Redis, while allowing the automated test suite to run locally without
external services.
"""

from __future__ import annotations

from config.settings import *  # noqa: F403

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",  # noqa: F405
        "ATOMIC_REQUESTS": True,
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "taskflow-tests",
    }
}

PASSWORD_HASHERS = [
    # MD5 first keeps test-created passwords fast; PBKDF2 is required so that
    # fixtures shipped with PBKDF2 hashes (e.g. taskflow_demo_data) can be
    # verified when running with these settings.
    "django.contrib.auth.hashers.MD5PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
