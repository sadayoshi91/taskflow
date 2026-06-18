"""Widoki API dla aplikacji zadan."""

from django.conf import settings
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tasks.models import Task
from apps.tasks.permissions import CanAccessTask
from apps.tasks.serializers import TaskDetailSerializer, TaskListSerializer, TaskWriteSerializer


ACTIVE_TASK_CACHE_KEY = "active_task_list"


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD API dla zadan."""

    queryset = Task.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated, CanAccessTask]

    def get_serializer_class(self):
        if self.action in ["list", "active"]:
            return TaskListSerializer
        if self.action == "retrieve":
            return TaskDetailSerializer
        return TaskWriteSerializer

    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request, *args, **kwargs):
        """Lista aktywnych zadan (z cache)."""
        data = cache.get(ACTIVE_TASK_CACHE_KEY)
        if data is None:
            queryset = self.get_queryset().exclude(status__in=[Task.Status.DONE, Task.Status.CANCELLED])
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            cache.set(ACTIVE_TASK_CACHE_KEY, response.data, settings.ACTIVE_TASK_LIST_CACHE_TIMEOUT)
            return response
        return Response(data)

    def perform_create(self, serializer):
        serializer.save()
        cache.delete(ACTIVE_TASK_CACHE_KEY)

    def perform_update(self, serializer):
        serializer.save()
        cache.delete(ACTIVE_TASK_CACHE_KEY)

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete(ACTIVE_TASK_CACHE_KEY)
