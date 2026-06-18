"""Data models for the tasks app."""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.projects.models import Project


class Task(models.Model):
    """Task assigned to a user and belonging to a project."""

    class Status(models.TextChoices):
        """Task lifecycle states."""

        TODO = "TODO", _("To do")
        IN_PROGRESS = "IN_PROGRESS", _("In progress")
        DONE = "DONE", _("Done")
        CANCELLED = "CANCELLED", _("Cancelled")

    class Priority(models.TextChoices):
        """Task urgency levels."""

        LOW = "LOW", _("Low")
        MEDIUM = "MEDIUM", _("Medium")
        HIGH = "HIGH", _("High")

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name=_("project"),
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        verbose_name=_("assigned to"),
        null=True,
        blank=True,
    )
    title = models.CharField(_("title"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    due_date = models.DateField(_("due date"))
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )
    priority = models.CharField(
        _("priority"),
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        """Model metadata."""

        verbose_name = _("task")
        verbose_name_plural = _("tasks")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status",)),
            models.Index(fields=("priority",)),
            models.Index(fields=("due_date",)),
        ]

    def __str__(self) -> str:
        """Return a readable task title."""
        return self.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Validate the task before saving it."""
        self.full_clean()
        super().save(*args, **kwargs)


class TaskNotification(models.Model):
    """A stored notification generated for a task reminder."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("task"),
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_notifications",
        verbose_name=_("recipient"),
    )
    message = models.TextField(_("message"))
    reminder_date = models.DateField(_("reminder date"))
    is_read = models.BooleanField(_("is read"), default=False)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        """Model metadata."""

        verbose_name = _("task notification")
        verbose_name_plural = _("task notifications")
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("task", "recipient", "reminder_date"),
                name="unique_task_notification_per_day",
            )
        ]

    def __str__(self) -> str:
        """Return a readable notification title."""
        return f"Notification for {self.recipient} about {self.task}"
