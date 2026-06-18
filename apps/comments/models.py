"""Data models for the comments app."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.tasks.models import Task


class Comment(models.Model):
    """A comment left by a user on a task."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("task"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("author"),
    )
    content = models.TextField(_("content"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        """Model metadata."""

        verbose_name = _("comment")
        verbose_name_plural = _("comments")
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=("created_at",)),
        ]

    def __str__(self) -> str:
        """Return a short readable comment representation."""
        return f"Comment by {self.author} on {self.task}"

