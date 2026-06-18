"""Widoki API dla aplikacji projektow."""

from django.conf import settings
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from apps.projects.models import Project
from apps.projects.serializers import ProjectDetailSerializer, ProjectListSerializer, ProjectWriteSerializer
from apps.users.models import User


PROJECT_LIST_CACHE_KEY = "project_list"


class CanManageProject(BasePermission):
    """Czytac moga wszyscy zalogowani, zmieniac kierownik i administrator."""

    message = "Nie masz uprawnien do zarzadzania projektami."

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.is_superuser or user.is_staff or user.role in [User.Role.ADMIN, User.Role.MANAGER]


class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD API dla projektow."""

    queryset = Project.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated, CanManageProject]

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        if self.action == "retrieve":
            return ProjectDetailSerializer
        return ProjectWriteSerializer

    def list(self, request, *args, **kwargs):
        """Lista projektow (z cache)."""
        data = cache.get(PROJECT_LIST_CACHE_KEY)
        if data is None:
            response = super().list(request, *args, **kwargs)
            cache.set(PROJECT_LIST_CACHE_KEY, response.data, settings.PROJECT_LIST_CACHE_TIMEOUT)
            return response
        return Response(data)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        cache.delete(PROJECT_LIST_CACHE_KEY)

    def perform_update(self, serializer):
        serializer.save()
        cache.delete(PROJECT_LIST_CACHE_KEY)

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete(PROJECT_LIST_CACHE_KEY)
