"""Podstawowe testy aplikacji uzytkownikow."""

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import UserProfile

User = get_user_model()


class UserModelTests(TestCase):
    """Testy modelu uzytkownika."""

    def test_create_user_creates_profile(self):
        user = User.objects.create_user("jan", "jan@example.com", "haslo12345")
        self.assertEqual(user.role, User.Role.EMPLOYEE)
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_create_superuser(self):
        admin = User.objects.create_superuser("admin", "admin@example.com", "haslo12345")
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, User.Role.ADMIN)


class UserApiTests(TestCase):
    """Testy API uzytkownikow i logowania JWT."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("ola", "ola@example.com", "haslo12345")

    def test_register_creates_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "nowy",
                "email": "nowy@example.com",
                "first_name": "Nowy",
                "last_name": "Uzytkownik",
                "password": "haslo12345",
                "password_confirm": "haslo12345",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="nowy").exists())

    def test_me_endpoint_returns_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "ola")

    def test_jwt_login_returns_token(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "ola", "password": "haslo12345"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)


class SeedDbCommandTests(TestCase):
    """Test komendy generujacej dane."""

    def test_seed_db_creates_data(self):
        call_command("seed_db", managers=1, employees=2, projects=1, max_tasks=2, max_comments=1, seed=1)
        self.assertTrue(User.objects.filter(role=User.Role.MANAGER).exists())
