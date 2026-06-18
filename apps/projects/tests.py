"""Podstawowe testy aplikacji projektow."""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.projects.models import Project

User = get_user_model()


class ProjectModelTests(TestCase):
    """Testy modelu projektu."""

    def setUp(self):
        self.manager = User.objects.create_user(
            "kierownik", "kierownik@example.com", "haslo12345", role=User.Role.MANAGER
        )

    def test_create_project(self):
        project = Project.objects.create(
            name="Projekt A",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            manager=self.manager,
            created_by=self.manager,
        )
        self.assertEqual(str(project), "Projekt A")
        self.assertEqual(project.status, Project.Status.PLANNED)


class ProjectApiTests(TestCase):
    """Testy API projektow."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("user", "user@example.com", "haslo12345")

    def test_anonymous_cannot_list_projects(self):
        response = self.client.get(reverse("project-list"))
        self.assertIn(response.status_code, [401, 403])

    def test_authenticated_user_can_list_projects(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("project-list"))
        self.assertEqual(response.status_code, 200)
