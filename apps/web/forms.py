"""Forms used by the TaskFlow web frontend."""

from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from apps.comments.models import Comment
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.users.models import UserProfile

User = get_user_model()


class WebAuthenticationForm(AuthenticationForm):
    """Authentication form tailored for the frontend login page."""

    username = forms.CharField(
        label=_("Username"),
           widget=forms.TextInput(),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
           widget=forms.PasswordInput(),
    )


class UserRegistrationForm(forms.Form):
    """Frontend registration form for new employee accounts."""

    username = forms.CharField(
        label=_("Username"),
        max_length=150,
           widget=forms.TextInput(),
    )
    email = forms.EmailField(
        label=_("Email"),
           widget=forms.EmailInput(),
    )
    first_name = forms.CharField(
        label=_("First name"),
        max_length=150,
        required=False,
           widget=forms.TextInput(),
    )
    last_name = forms.CharField(
        label=_("Last name"),
        max_length=150,
        required=False,
           widget=forms.TextInput(),
    )
    password1 = forms.CharField(
        label=_("Password"),
           widget=forms.PasswordInput(),
    )
    password2 = forms.CharField(
        label=_("Repeat password"),
           widget=forms.PasswordInput(),
    )

    def clean_username(self) -> str:
        """Ensure the username is unique."""
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_("A user with this username already exists."))
        return username

    def clean_email(self) -> str:
        """Ensure the email is unique."""
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("A user with this email already exists."))
        return email

    def clean(self) -> dict[str, str]:
        """Validate password confirmation."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", _("Passwords do not match."))
        return cleaned_data


class ProfileForm(forms.ModelForm):
    """Form for editing the current user's profile, including the avatar image."""

    class Meta:
        model = UserProfile
        fields = ("avatar", "job_title", "phone_number", "bio")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }


class ProjectForm(forms.ModelForm):
    """Create and edit projects from the web frontend."""

    class Meta:
        model = Project
        fields = ("name", "description", "start_date", "end_date", "status", "manager")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Manager can be any manager or admin.
        self.fields["manager"].queryset = User.objects.filter(
            role__in=[User.Role.MANAGER, User.Role.ADMIN]
        )
        # Native date inputs need the ISO format.
        self.fields["start_date"].input_formats = ["%Y-%m-%d"]
        self.fields["end_date"].input_formats = ["%Y-%m-%d"]


class TaskForm(forms.ModelForm):
    """Create and edit tasks from the web frontend."""

    class Meta:
        model = Task
        fields = ("project", "title", "description", "assigned_to", "due_date", "status", "priority")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "due_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].required = False
        self.fields["assigned_to"].empty_label = "— nieprzypisane —"
        self.fields["due_date"].input_formats = ["%Y-%m-%d"]


class TaskStatusForm(forms.ModelForm):
    """Minimal form used for the quick status change on the task detail page."""

    class Meta:
        model = Task
        fields = ("status",)


class CommentForm(forms.ModelForm):
    """Add a comment to a task."""

    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3, "placeholder": "Napisz komentarz..."}),
        }
        labels = {"content": _("Komentarz")}
