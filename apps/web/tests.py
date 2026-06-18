"""Podstawowe testy frontendu (widoki HTML)."""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.comments.models import Comment
from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


class WebPageTests(TestCase):
    """Testy stron HTML."""

    def setUp(self):
        self.manager = User.objects.create_user(
            "kier", "kier@example.com", "haslo12345", role=User.Role.MANAGER
        )
        self.employee = User.objects.create_user("prac", "prac@example.com", "haslo12345")

    def test_login_page_returns_200(self):
        response = self.client.get(reverse("web-login"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirects_anonymous(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_dashboard_for_logged_in_user(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")

    def test_project_and_task_list_pages(self):
        self.client.force_login(self.manager)
        self.assertEqual(self.client.get(reverse("project-list-page")).status_code, 200)
        self.assertEqual(self.client.get(reverse("task-list-page")).status_code, 200)

    def test_register_creates_user(self):
        response = self.client.post(
            reverse("web-register"),
            {
                "username": "nowy",
                "email": "nowy@example.com",
                "first_name": "Nowy",
                "last_name": "Uzytkownik",
                "password1": "haslo12345",
                "password2": "haslo12345",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="nowy").exists())


class WebCrudTests(TestCase):
    """Testy tworzenia danych i uprawnien w widokach HTML."""

    def setUp(self):
        self.manager = User.objects.create_user(
            "kier", "kier@example.com", "haslo12345", role=User.Role.MANAGER
        )
        self.employee = User.objects.create_user("prac", "prac@example.com", "haslo12345")
        self.project = Project.objects.create(
            name="Projekt",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=20),
            manager=self.manager,
            created_by=self.manager,
        )
        self.task = Task.objects.create(
            project=self.project,
            assigned_to=self.employee,
            title="Zadanie",
            due_date=date.today() + timedelta(days=5),
        )

    def test_manager_can_create_project(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            reverse("project-create-page"),
            {
                "name": "Nowy projekt",
                "description": "Opis",
                "start_date": date.today().isoformat(),
                "end_date": (date.today() + timedelta(days=10)).isoformat(),
                "status": Project.Status.PLANNED,
                "manager": self.manager.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name="Nowy projekt").exists())

    def test_employee_cannot_create_project(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse("project-create-page"))
        self.assertEqual(response.status_code, 403)

    def test_user_can_add_comment(self):
        self.client.force_login(self.employee)
        response = self.client.post(
            reverse("task-comment-page", args=[self.task.pk]),
            {"content": "Moj komentarz"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(content="Moj komentarz").exists())

    def test_assigned_employee_can_change_status(self):
        self.client.force_login(self.employee)
        response = self.client.post(
            reverse("task-status-page", args=[self.task.pk]),
            {"status": Task.Status.DONE},
        )
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.DONE)
