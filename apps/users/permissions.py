"""Role-based permissions for the users app."""

from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.users.models import User


class IsAdministrator(BasePermission):
    """Allow access only to administrative users."""

    message = "You must be an administrator to access this resource."

    def has_permission(self, request: Any, view: Any) -> bool:
        """Check if the current user has administrative rights."""
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.is_staff or getattr(user, "role", None) == User.Role.ADMIN)
        )


class IsOwnerOrAdministrator(BasePermission):
    """Allow access to the owner of the object or an administrator."""

    message = "You do not have permission to access this resource."

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        """Check ownership or elevated access on a specific object."""
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser or user.is_staff or getattr(user, "role", None) == User.Role.ADMIN:
            return True

        owner = getattr(obj, "user", obj)
        owner_pk = getattr(owner, "pk", None)
        return owner_pk == user.pk


class IsAuthenticatedOrReadOnly(BasePermission):
    """Allow authenticated writes and public read-only access."""

    message = "Authentication is required for write operations."

    def has_permission(self, request: Any, view: Any) -> bool:
        """Allow safe methods for everyone and writes for authenticated users."""
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

