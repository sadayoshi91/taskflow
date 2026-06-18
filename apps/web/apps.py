"""Application configuration for the web frontend."""

from __future__ import annotations

from django.apps import AppConfig


class WebConfig(AppConfig):
    """Configuration for the web frontend app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.web"
    verbose_name = "Web Frontend"

