"""Application configuration for the comments module."""

from __future__ import annotations

from django.apps import AppConfig


class CommentsConfig(AppConfig):
    """Configuration for the comments app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.comments"
    verbose_name = "Comments"

