"""Data models for the users app."""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom manager for the project user model."""

    use_in_migrations = True

    def _create_user(self, username: str, email: str, password: str | None, **extra_fields: Any) -> "User":
        """Create and save a user with the given credentials."""
        if not username:
            raise ValueError("The username must be set.")
        if not email:
            raise ValueError("The email must be set.")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        username: str,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        """Create a regular user."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", User.Role.EMPLOYEE)
        return self._create_user(username=username, email=email, password=password, **extra_fields)

    def create_superuser(
        self,
        username: str,
        email: str,
        password: str | None,
        **extra_fields: Any,
    ) -> "User":
        """Create a superuser with administrative privileges."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username=username, email=email, password=password, **extra_fields)


class User(AbstractUser):
    """Custom application user with role-based access."""

    class Role(models.TextChoices):
        """Business roles used across the application."""

        ADMIN = "ADMIN", _("Administrator")
        MANAGER = "MANAGER", _("Kierownik")
        EMPLOYEE = "EMPLOYEE", _("Pracownik")

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )

    objects = UserManager()

    class Meta:
        """Model metadata."""

        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ("username",)

    def __str__(self) -> str:
        """Return the canonical string representation."""
        return self.get_full_name() or self.username

    @property
    def is_admin_role(self) -> bool:
        """Return whether the user has an administrator role."""
        return self.role == self.Role.ADMIN

    @property
    def is_manager_role(self) -> bool:
        """Return whether the user has a manager role."""
        return self.role == self.Role.MANAGER

    @property
    def is_employee_role(self) -> bool:
        """Return whether the user has an employee role."""
        return self.role == self.Role.EMPLOYEE

    @property
    def full_name(self) -> str:
        """Return a full name fallback friendly to empty names."""
        full_name = self.get_full_name().strip()
        return full_name if full_name else self.username

    @property
    def can_manage_users(self) -> bool:
        """Return whether the user may administer the user base."""
        return self.is_superuser or self.is_staff or self.is_admin_role

    @property
    def can_manage_work(self) -> bool:
        """Czy uzytkownik moze zarzadzac projektami i zadaniami (admin/kierownik)."""
        return self.is_superuser or self.is_admin_role or self.is_manager_role


class UserProfile(models.Model):
    """Extended profile information for a user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("user"),
    )
    phone_number = models.CharField(_("phone number"), max_length=32, blank=True)
    job_title = models.CharField(_("job title"), max_length=120, blank=True)
    avatar = models.ImageField(
        _("avatar"),
        upload_to="avatars/",
        blank=True,
        null=True,
        help_text=_("Profile picture uploaded by the user."),
    )
    avatar_url = models.URLField(_("avatar url"), blank=True)
    bio = models.TextField(_("bio"), blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        """Model metadata."""

        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")
        ordering = ("user__username",)

    def __str__(self) -> str:
        """Return a readable representation for admin/debugging."""
        return f"{self.user.username} profile"

    @property
    def avatar_display_url(self) -> str:
        """Return the best available avatar source for templates.

        Prefers an uploaded image file, then falls back to the external
        avatar URL, and finally to an empty string when neither is set.
        """
        if self.avatar:
            return self.avatar.url
        return self.avatar_url or ""


@receiver(post_save, sender=User)
def create_user_profile(sender: type[User], instance: User, created: bool, **kwargs: Any) -> None:
    """Create an empty profile for every new user."""
    if created and not kwargs.get("raw", False):
        UserProfile.objects.create(user=instance)

