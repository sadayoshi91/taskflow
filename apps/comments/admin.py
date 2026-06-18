"""Admin configuration for the comments app."""

from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for comment management."""

    list_display = ("task", "author", "short_content", "created_at")
    list_filter = ("created_at",)
    search_fields = ("content", "author__username", "author__email", "task__title", "task__project__name")
    autocomplete_fields = ("task", "author")
    ordering = ("-created_at",)

    @admin.display(description=_("Content"))
    def short_content(self, obj: Comment) -> str:
        """Return a truncated, single-line preview of the comment content."""
        text = obj.content.strip().replace("\n", " ")
        return text if len(text) <= 60 else f"{text[:57]}..."

