"""Celery application configuration for the TaskFlow project."""

from __future__ import annotations

import os

from celery import Celery
from django.conf import settings as django_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("taskflow")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = django_settings.CELERY_BEAT_SCHEDULE
app.conf.timezone = django_settings.TIME_ZONE


@app.task(bind=True)
def debug_task(self) -> str:
    """Return a small debug message useful during Celery setup."""
    return f"Debug task executed: {self.request!r}"
