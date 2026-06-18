"""API views for the users app."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers, viewsets
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.models import UserProfile
from apps.users.permissions import IsAdministrator, IsOwnerOrAdministrator
from apps.users.serializers import (
    CurrentUserSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserWriteSerializer,
)

User = get_user_model()


class RegistrationView(CreateAPIView):
    """Allow anonymous visitors to create employee accounts."""

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []


class LoginView(TokenObtainPairView):
    """Expose the JWT login endpoint under the app namespace."""


class RefreshTokenView(TokenRefreshView):
    """Expose the JWT refresh endpoint under the app namespace."""


class CurrentUserView(RetrieveUpdateAPIView):
    """Return and update the authenticated user's own account."""

    serializer_class = CurrentUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        """Return the authenticated user instance."""
        return self.request.user


class UserProfileView(RetrieveUpdateAPIView):
    """Return and update a profile by user identifier."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdministrator]

    def get_object(self) -> UserProfile:
        """Resolve the profile for the requested user."""
        user = get_object_or_404(User.objects.select_related("profile"), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, user)
        return user.profile


class UserViewSet(viewsets.ModelViewSet):
    """Full CRUD for user accounts."""

    queryset = User.objects.select_related("profile").all()
    permission_classes = [IsAuthenticated, IsAdministrator]

    def get_serializer_class(self) -> type[serializers.Serializer]:
        """Select a serializer depending on the current action."""
        if self.action == "list":
            return UserListSerializer
        if self.action in {"create", "update", "partial_update"}:
            return UserWriteSerializer
        return UserDetailSerializer

    def get_queryset(self):
        """Return the base queryset with related profile data."""
        return super().get_queryset().order_by("username")
