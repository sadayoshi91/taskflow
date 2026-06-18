"""Serializers for the users app."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from apps.users.models import UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serialize profile data for a user."""

    class Meta:
        """Serializer metadata."""

        model = UserProfile
        fields = (
            "phone_number",
            "job_title",
            "avatar",
            "avatar_url",
            "bio",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("avatar", "created_at", "updated_at")


class UserListSerializer(serializers.ModelSerializer):
    """Serialize a compact user representation for list endpoints."""

    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        """Serializer metadata."""

        model = User
        fields = (
            "id",
            "username",
            "email",
            "full_name",
            "role",
            "role_display",
            "is_active",
        )


class UserDetailSerializer(serializers.ModelSerializer):
    """Serialize a detailed user representation."""

    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        """Serializer metadata."""

        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "role_display",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "profile",
        )
        read_only_fields = ("date_joined", "last_login", "is_superuser")


class UserWriteSerializer(serializers.ModelSerializer):
    """Serialize user data for create and update operations."""

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        style={"input_type": "password"},
    )
    profile = UserProfileSerializer(required=False)

    class Meta:
        """Serializer metadata."""

        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_staff",
            "password",
            "profile",
        )
        read_only_fields = ("id",)

    def _update_profile(self, user: User, profile_data: dict[str, Any]) -> None:
        """Update the associated profile with validated nested data."""
        if not profile_data:
            return

        profile, _ = UserProfile.objects.get_or_create(user=user)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        user.profile = profile

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> User:
        """Create a user and optionally update the generated profile."""
        profile_data = validated_data.pop("profile", {})
        password = validated_data.pop("password", None)

        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        self._update_profile(user=user, profile_data=profile_data)
        return user

    @transaction.atomic
    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Update a user and optionally its profile."""
        profile_data = validated_data.pop("profile", {})
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()

        self._update_profile(user=instance, profile_data=profile_data)
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serialize data used during self-registration."""

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        """Serializer metadata."""

        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        )

    def validate_email(self, value: str) -> str:
        """Ensure the email address is unique in a case-insensitive manner."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value: str) -> str:
        """Ensure the username is unique in a case-insensitive manner."""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate password confirmation."""
        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm", None)
        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> User:
        """Create a new employee account for self-registration."""
        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password")
        validated_data.setdefault("role", User.Role.EMPLOYEE)
        user = User.objects.create_user(password=password, **validated_data)
        return user


class CurrentUserSerializer(serializers.ModelSerializer):
    """Serialize the authenticated user's own data."""

    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    profile = UserProfileSerializer(required=False)
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        style={"input_type": "password"},
    )

    class Meta:
        """Serializer metadata."""

        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "role_display",
            "password",
            "profile",
        )
        read_only_fields = ("id", "role", "role_display")

    def _update_profile(self, user: User, profile_data: dict[str, Any]) -> None:
        """Update the associated profile with validated nested data."""
        if not profile_data:
            return

        profile, _ = UserProfile.objects.get_or_create(user=user)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        user.profile = profile

    @transaction.atomic
    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Update the authenticated user's account and profile."""
        profile_data = validated_data.pop("profile", {})
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()

        self._update_profile(user=instance, profile_data=profile_data)
        return instance

