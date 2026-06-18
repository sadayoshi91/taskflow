"""URL configuration for the users app."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views import (
    CurrentUserView,
    LoginView,
    RefreshTokenView,
    RegistrationView,
    UserProfileView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("auth/register/", RegistrationView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("auth/me/", CurrentUserView.as_view(), name="me"),
    path("profile/", CurrentUserView.as_view(), name="profile"),
    path("users/<int:pk>/profile/", UserProfileView.as_view(), name="user-profile"),
    path("", include(router.urls)),
]
