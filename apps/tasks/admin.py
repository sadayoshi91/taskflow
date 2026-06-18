"""Admin configuration for the tasks app."""

from __future__ import annotations

from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.tasks.models import Task, TaskNotification


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for task management."""

    list_display = (
        "title",
        "project",
        "assigned_to",
        "status",
        "priority",
        "due_date",
        "is_overdue",
        "comment_count",
        "created_at",
    )
    list_filter = ("status", "priority", "due_date", "created_at", "updated_at")
    search_fields = ("title", "description", "project__name", "assigned_to__username", "assigned_to__email")
    autocomplete_fields = ("project", "assigned_to")
    ordering = ("-created_at",)
    date_hierarchy = "due_date"

    def get_queryset(self, request: HttpRequest) -> QuerySet[Task]:
        """Annotate the task queryset with the number of related comments."""
        return super().get_queryset(request).annotate(_comment_count=Count("comments"))

    @admin.display(description=_("Comments"), ordering="_comment_count")
    def comment_count(self, obj: Task) -> int:
        """Return the number of comments left on the task."""
        return getattr(obj, "_comment_count", obj.comments.count())

    @admin.display(description=_("Overdue"), boolean=True)
    def is_overdue(self, obj: Task) -> bool:
        """Return whether the task is past its due date and still open."""
        open_statuses = {Task.Status.TODO, Task.Status.IN_PROGRESS}
        return bool(obj.due_date and obj.due_date < timezone.localdate() and obj.status in open_statuses)


@admin.register(TaskNotification)
class TaskNotificationAdmin(admin.ModelAdmin):
    """Admin interface for reminder notifications."""

    list_display = ("task", "recipient", "reminder_date", "is_read", "created_at")
    list_filter = ("is_read", "reminder_date", "created_at")
    search_fields = ("task__title", "recipient__username", "recipient__email", "message")
    autocomplete_fields = ("task", "recipient")
    ordering = ("-created_at",)
