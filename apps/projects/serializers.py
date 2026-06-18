"""Serializers for the projects app."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.projects.models import Project

User = get_user_model()


class ProjectListSerializer(serializers.ModelSerializer):
    """Serialize a compact project representation for list endpoints."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    manager_username = serializers.CharField(source="manager.username", read_only=True)
    manager_full_name = serializers.CharField(source="manager.full_name", read_only=True)

    class Meta:
        """Serializer metadata."""

        model = Project
        fields = (
            "id",
            "name",
            "status",
            "status_display",
            "manager",
            "manager_username",
            "manager_full_name",
            "start_date",
            "end_date",
            "created_at",
        )


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serialize a detailed project representation."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    manager_username = serializers.CharField(source="manager.username", read_only=True)
    manager_full_name = serializers.CharField(source="manager.full_name", read_only=True)
    created_by_username = serializers.SerializerMethodField()
    created_by_full_name = serializers.SerializerMethodField()

    class Meta:
        """Serializer metadata."""

        model = Project
        fields = (
            "id",
            "name",
            "description",
            "status",
            "status_display",
            "manager",
            "manager_username",
            "manager_full_name",
            "created_by",
            "created_by_username",
            "created_by_full_name",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
        )

    def get_created_by_username(self, obj: Project) -> str | None:
        """Return the creator username when available."""
        if obj.created_by is None:
            return None
        return obj.created_by.username

    def get_created_by_full_name(self, obj: Project) -> str | None:
        """Return the creator full name when available."""
        if obj.created_by is None:
            return None
        return obj.created_by.full_name


class ProjectWriteSerializer(serializers.ModelSerializer):
    """Serialize project data for create and update operations."""

    manager = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        """Serializer metadata."""

        model = Project
        fields = (
            "id",
            "name",
            "description",
            "start_date",
            "end_date",
            "status",
            "manager",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def validate_manager(self, value: User) -> User:
        """Ensure the selected manager has an allowed role."""
        if value.role not in {User.Role.ADMIN, User.Role.MANAGER}:
            raise serializers.ValidationError("Project manager must have a manager or administrator role.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate date consistency and manager assignment rules."""
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "End date cannot be earlier than start date."})

        request = self.context.get("request")
        current_user = getattr(request, "user", None)
        manager = attrs.get("manager")

        if current_user and current_user.is_authenticated:
            if current_user.role == User.Role.MANAGER:
                if manager is None:
                    attrs["manager"] = current_user
                elif manager.pk != current_user.pk:
                    raise serializers.ValidationError({"manager": "Managers can only assign themselves as project manager."})
            elif manager is None and self.instance is None:
                raise serializers.ValidationError({"manager": "Manager is required for project creation."})

        return attrs

    def create(self, validated_data: dict[str, Any]) -> Project:
        """Create a project and set the creator automatically when possible."""
        created_by = validated_data.pop("created_by", None)
        request = self.context.get("request")
        if created_by is None and request is not None and getattr(request, "user", None) and request.user.is_authenticated:
            created_by = request.user

        if "manager" not in validated_data and request is not None and getattr(request, "user", None) and request.user.is_authenticated:
            if request.user.role == User.Role.MANAGER:
                validated_data["manager"] = request.user

        return Project.objects.create(created_by=created_by, **validated_data)

    def update(self, instance: Project, validated_data: dict[str, Any]) -> Project:
        """Update an existing project."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
