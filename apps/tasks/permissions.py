"""Uprawnienia dla aplikacji zadan."""

from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.users.models import User


class CanAccessTask(BasePermission):
    """Czytac moga wszyscy zalogowani, zmieniac kierownik i administrator."""

    message = "Nie masz uprawnien do tej operacji."

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.is_superuser or user.is_staff or user.role in [User.Role.ADMIN, User.Role.MANAGER]
