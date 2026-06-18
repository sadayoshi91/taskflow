"""Admin configuration for the projects app."""

from __future__ import annotations

from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for project management."""

    list_display = (
        "name",
        "status",
        "manager",
        "created_by",
        "task_count",
        "duration_days",
        "start_date",
        "end_date",
        "created_at",
    )
    list_filter = ("status", "start_date", "end_date", "created_at", "updated_at")
    search_fields = ("name", "description", "manager__username", "manager__email")
    autocomplete_fields = ("manager", "created_by")
    ordering = ("-created_at",)
    date_hierarchy = "start_date"

    def get_queryset(self, request: HttpRequest) -> QuerySet[Project]:
        """Annotate the project queryset with the number of related tasks."""
        return super().get_queryset(request).annotate(_task_count=Count("tasks"))

    @admin.display(description=_("Tasks"), ordering="_task_count")
    def task_count(self, obj: Project) -> int:
        """Return the number of tasks attached to the project."""
        return getattr(obj, "_task_count", obj.tasks.count())

    @admin.display(description=_("Duration (days)"))
    def duration_days(self, obj: Project) -> str:
        """Return the project length in days based on start and end dates."""
        if obj.start_date and obj.end_date:
            return str((obj.end_date - obj.start_date).days)
        return "-"

