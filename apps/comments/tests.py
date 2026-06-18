"""Podstawowe testy aplikacji komentarzy."""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.comments.models import Comment
from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


class CommentTests(TestCase):
    """Testy komentarzy."""

    def setUp(self):
        self.client = APIClient()
        self.manager = User.objects.create_user(
            "kier", "kier@example.com", "haslo12345", role=User.Role.MANAGER
        )
        self.project = Project.objects.create(
            name="Projekt",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            manager=self.manager,
            created_by=self.manager,
        )
        self.task = Task.objects.create(
            project=self.project,
            title="Zadanie",
            due_date=date.today() + timedelta(days=2),
        )

    def test_create_comment(self):
        comment = Comment.objects.create(task=self.task, author=self.manager, content="Tresc")
        self.assertEqual(comment.content, "Tresc")
        self.assertEqual(self.task.comments.count(), 1)

    def test_authenticated_user_can_list_comments(self):
        self.client.force_authenticate(self.manager)
        response = self.client.get(reverse("comment-list"))
        self.assertEqual(response.status_code, 200)
