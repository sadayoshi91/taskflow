"""Widoki API dla aplikacji komentarzy."""

from rest_framework import viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.comments.models import Comment
from apps.comments.serializers import CommentDetailSerializer, CommentListSerializer, CommentWriteSerializer


class CanAccessComment(BasePermission):
    """Komentarze sa dostepne dla kazdego zalogowanego uzytkownika."""

    message = "Musisz byc zalogowany, aby korzystac z komentarzy."

    def has_permission(self, request, view):
        return request.user.is_authenticated


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD API dla komentarzy."""

    queryset = Comment.objects.all().order_by("created_at")
    permission_classes = [IsAuthenticated, CanAccessComment]

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        if self.action == "retrieve":
            return CommentDetailSerializer
        return CommentWriteSerializer
