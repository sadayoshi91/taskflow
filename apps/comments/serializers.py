"""Serializers for the comments app."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.comments.models import Comment
from apps.tasks.models import Task

User = get_user_model()


class CommentListSerializer(serializers.ModelSerializer):
    """Serialize a compact comment representation."""

    author_username = serializers.CharField(source="author.username", read_only=True)
    author_full_name = serializers.CharField(source="author.full_name", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)
    project_name = serializers.CharField(source="task.project.name", read_only=True)

    class Meta:
        """Serializer metadata."""

        model = Comment
        fields = (
            "id",
            "task",
            "task_title",
            "project_name",
            "author",
            "author_username",
            "author_full_name",
            "content",
            "created_at",
        )


class CommentDetailSerializer(serializers.ModelSerializer):
    """Serialize a detailed comment representation."""

    author_username = serializers.CharField(source="author.username", read_only=True)
    author_full_name = serializers.CharField(source="author.full_name", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)
    project_name = serializers.CharField(source="task.project.name", read_only=True)
    project_manager_username = serializers.CharField(source="task.project.manager.username", read_only=True)
    task_assigned_to_username = serializers.SerializerMethodField()

    class Meta:
        """Serializer metadata."""

        model = Comment
        fields = (
            "id",
            "task",
            "task_title",
            "project_name",
            "project_manager_username",
            "author",
            "author_username",
            "author_full_name",
            "task_assigned_to_username",
            "content",
            "created_at",
        )

    def get_task_assigned_to_username(self, obj: Comment) -> str | None:
        """Return the assigned user's username when available."""
        if obj.task.assigned_to is None:
            return None
        return obj.task.assigned_to.username


class CommentWriteSerializer(serializers.ModelSerializer):
    """Serialize comment data for create and update operations."""

    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.select_related("project", "project__manager", "assigned_to").all())

    class Meta:
        """Serializer metadata."""

        model = Comment
        fields = (
            "id",
            "task",
            "author",
            "content",
            "created_at",
        )
        read_only_fields = ("id", "author", "created_at")

    def validate_task(self, value: Task) -> Task:
        """Ensure the current user can comment on the selected task."""
        request = self.context.get("request")
        current_user = getattr(request, "user", None)
        if current_user is None or not current_user.is_authenticated:
            raise serializers.ValidationError("Authentication is required.")

        if current_user.is_superuser or current_user.is_staff or current_user.role == User.Role.ADMIN:
            return value

        if current_user.role == User.Role.MANAGER:
            if value.project.manager_id != current_user.id:
                raise serializers.ValidationError("Managers can only comment on tasks in their own projects.")
            return value

        if current_user.role == User.Role.EMPLOYEE:
            if value.assigned_to_id != current_user.id:
                raise serializers.ValidationError("Employees can only comment on tasks assigned to them.")
            return value

        raise serializers.ValidationError("You do not have permission to comment on this task.")

    def create(self, validated_data: dict[str, Any]) -> Comment:
        """Create a new comment and assign the current user as author."""
        request = self.context.get("request")
        author = getattr(request, "user", None)
        return Comment.objects.create(author=author, **validated_data)

    def update(self, instance: Comment, validated_data: dict[str, Any]) -> Comment:
        """Update an existing comment's content."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

