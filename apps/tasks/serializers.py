"""Serializers for the tasks app."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


class TaskListSerializer(serializers.ModelSerializer):
    """Serialize a compact task representation."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    assigned_to_username = serializers.SerializerMethodField()

    class Meta:
        """Serializer metadata."""

        model = Task
        fields = (
            "id",
            "title",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "project",
            "project_name",
            "assigned_to",
            "assigned_to_username",
            "due_date",
            "created_at",
        )

    def get_assigned_to_username(self, obj: Task) -> str | None:
        """Return the username of the assigned user when available."""
        if obj.assigned_to is None:
            return None
        return obj.assigned_to.username


class TaskDetailSerializer(serializers.ModelSerializer):
    """Serialize a detailed task representation."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    project_status_display = serializers.CharField(source="project.get_status_display", read_only=True)
    assigned_to_username = serializers.SerializerMethodField()
    assigned_to_full_name = serializers.SerializerMethodField()

    class Meta:
        """Serializer metadata."""

        model = Task
        fields = (
            "id",
            "title",
            "description",
            "due_date",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "project",
            "project_name",
            "project_status_display",
            "assigned_to",
            "assigned_to_username",
            "assigned_to_full_name",
            "created_at",
            "updated_at",
        )

    def get_assigned_to_full_name(self, obj: Task) -> str | None:
        """Return the full name of the assigned user when available."""
        if obj.assigned_to is None:
            return None
        return obj.assigned_to.full_name

    def get_assigned_to_username(self, obj: Task) -> str | None:
        """Return the username of the assigned user when available."""
        if obj.assigned_to is None:
            return None
        return obj.assigned_to.username


class TaskWriteSerializer(serializers.ModelSerializer):
    """Serialize task data for create and update operations."""

    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.select_related("manager").all())
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        """Serializer metadata."""

        model = Task
        fields = (
            "id",
            "project",
            "assigned_to",
            "title",
            "description",
            "due_date",
            "status",
            "priority",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_project(self, value: Project) -> Project:
        """Ensure the selected project can receive tasks from the current user."""
        request = self.context.get("request")
        current_user = getattr(request, "user", None)
        if current_user and current_user.is_authenticated and current_user.role == User.Role.MANAGER:
            if value.manager_id != current_user.id:
                raise serializers.ValidationError("Managers can only create tasks in their own projects.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate business rules for the task payload."""
        request = self.context.get("request")
        current_user = getattr(request, "user", None)
        project = attrs.get("project", getattr(self.instance, "project", None))
        assigned_to = attrs.get("assigned_to", getattr(self.instance, "assigned_to", None))

        if current_user and current_user.is_authenticated:
            if current_user.role == User.Role.MANAGER and project is not None and project.manager_id != current_user.id:
                raise serializers.ValidationError({"project": "Managers can only manage tasks in their own projects."})

            if current_user.role == User.Role.EMPLOYEE:
                raise serializers.ValidationError("Employees cannot create or edit tasks.")

        return attrs

    def create(self, validated_data: dict[str, Any]) -> Task:
        """Create a new task."""
        return Task.objects.create(**validated_data)

    def update(self, instance: Task, validated_data: dict[str, Any]) -> Task:
        """Update an existing task."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
