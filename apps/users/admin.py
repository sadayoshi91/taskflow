"""Admin configuration for the users app."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.users.models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """Display the one-to-one profile inside the user admin."""

    model = UserProfile
    extra = 0
    can_delete = False
    verbose_name_plural = "Profile"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Custom admin for the project user model."""

    inlines = [UserProfileInline]
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Role and permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "role"),
            },
        ),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin view for the extended user profile."""

    list_display = ("user", "avatar_preview", "job_title", "phone_number", "updated_at")
    search_fields = ("user__username", "user__email", "job_title", "phone_number")
    list_filter = ("updated_at",)
    readonly_fields = ("avatar_preview",)

    @admin.display(description=_("Avatar"))
    def avatar_preview(self, obj: UserProfile) -> str:
        """Render a small thumbnail of the avatar image in the admin."""
        url = obj.avatar_display_url
        if url:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover;border-radius:50%;">', url)
        return "-"

