"""Podstawowe testy aplikacji zadan."""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.tasks.models import Task, TaskNotification
from apps.tasks.tasks import send_due_task_reminders

User = get_user_model()


def make_project(manager):
    return Project.objects.create(
        name="Projekt",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
        manager=manager,
        created_by=manager,
    )


class TaskModelTests(TestCase):
    """Testy modelu zadania."""

    def setUp(self):
        self.manager = User.objects.create_user(
            "kier", "kier@example.com", "haslo12345", role=User.Role.MANAGER
        )
        self.project = make_project(self.manager)

    def test_create_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Zadanie 1",
            due_date=date.today() + timedelta(days=3),
        )
        self.assertEqual(str(task), "Zadanie 1")
        self.assertEqual(task.status, Task.Status.TODO)


class TaskApiTests(TestCase):
    """Testy API zadan."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("user", "user@example.com", "haslo12345")

    def test_active_endpoint_returns_200(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("task-active"))
        self.assertEqual(response.status_code, 200)


class ReminderTaskTests(TestCase):
    """Test zadania Celery generujacego przypomnienia."""

    def test_reminder_creates_notification(self):
        manager = User.objects.create_user(
            "m", "m@example.com", "haslo12345", role=User.Role.MANAGER
        )
        employee = User.objects.create_user("e", "e@example.com", "haslo12345")
        project = make_project(manager)
        Task.objects.create(
            project=project,
            assigned_to=employee,
            title="Pilne",
            due_date=date.today() + timedelta(days=1),
        )

        created = send_due_task_reminders()

        self.assertGreaterEqual(created, 1)
        self.assertTrue(TaskNotification.objects.filter(recipient=employee).exists())
