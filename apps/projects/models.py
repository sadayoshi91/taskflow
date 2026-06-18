"""Data models for the projects app."""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    """Project entity managed by a manager and assigned to tasks."""

    class Status(models.TextChoices):
        """Lifecycle states for a project."""

        PLANNED = "PLANNED", _("Planned")
        ACTIVE = "ACTIVE", _("Active")
        ON_HOLD = "ON_HOLD", _("On hold")
        COMPLETED = "COMPLETED", _("Completed")
        CANCELLED = "CANCELLED", _("Cancelled")

    name = models.CharField(_("name"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="managed_projects",
        verbose_name=_("manager"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_projects",
        verbose_name=_("created by"),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        """Model metadata."""

        verbose_name = _("project")
        verbose_name_plural = _("projects")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status",)),
            models.Index(fields=("manager",)),
        ]

    def __str__(self) -> str:
        """Return the project name."""
        return self.name

    def clean(self) -> None:
        """Validate the model level business rules."""
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": _("End date cannot be earlier than start date.")})

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Validate the project before persisting it."""
        self.full_clean()
        super().save(*args, **kwargs)

