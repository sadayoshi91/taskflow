"""Application configuration for the projects module."""

from __future__ import annotations

from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """Configuration for the projects app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.projects"
    verbose_name = "Projects"

