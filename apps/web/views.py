"""Widoki strony WWW (frontend)."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from apps.projects.models import Project
from apps.tasks.models import Task
from apps.users.models import User, UserProfile
from apps.web.forms import (
    CommentForm,
    ProfileForm,
    ProjectForm,
    TaskForm,
    TaskStatusForm,
    UserRegistrationForm,
    WebAuthenticationForm,
)


def status_stats(queryset, field, choices):
    """Policz ile rekordow ma kazdy status/priorytet (dane do wykresow)."""
    total = queryset.count()
    stats = []
    for code, label in choices:
        count = queryset.filter(**{field: code}).count()
        pct = round(count / total * 100) if total else 0
        stats.append({"code": code, "label": label, "count": count, "pct": pct})
    return stats


class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Tylko zalogowany kierownik lub administrator moze zarzadzac danymi."""

    def test_func(self):
        return self.request.user.can_manage_work


class DashboardView(LoginRequiredMixin, TemplateView):
    """Strona glowna z podsumowaniem."""

    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = Project.objects.all()
        tasks = Task.objects.all()

        project_count = projects.count()
        task_count = tasks.count()
        completed_project_count = projects.filter(status=Project.Status.COMPLETED).count()
        done_task_count = tasks.filter(status=Task.Status.DONE).count()

        context["project_count"] = project_count
        context["active_project_count"] = projects.exclude(status=Project.Status.COMPLETED).count()
        context["task_count"] = task_count
        context["active_task_count"] = tasks.exclude(
            status__in=[Task.Status.DONE, Task.Status.CANCELLED]
        ).count()
        context["completed_project_count"] = completed_project_count
        context["done_task_count"] = done_task_count
        context["completed_project_pct"] = round(completed_project_count / project_count * 100) if project_count else 0
        context["done_task_pct"] = round(done_task_count / task_count * 100) if task_count else 0

        context["project_status_stats"] = status_stats(projects, "status", Project.Status.choices)
        context["task_status_stats"] = status_stats(tasks, "status", Task.Status.choices)
        context["task_priority_stats"] = status_stats(tasks, "priority", Task.Priority.choices)

        context["latest_projects"] = projects.order_by("-created_at")[:4]
        context["latest_tasks"] = tasks.order_by("-created_at")[:6]
        context["upcoming_tasks"] = tasks.exclude(
            status__in=[Task.Status.DONE, Task.Status.CANCELLED]
        ).order_by("due_date")[:5]
        return context


class ProjectListView(LoginRequiredMixin, ListView):
    """Lista projektow."""

    template_name = "project_list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        return Project.objects.annotate(task_total=Count("tasks")).order_by("-created_at", "name")


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """Szczegoly projektu."""

    template_name = "project_detail.html"
    context_object_name = "project"
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = self.object.tasks.order_by("due_date", "-created_at")
        context["can_edit"] = self.request.user.can_manage_work
        return context


class TaskListView(LoginRequiredMixin, ListView):
    """Lista zadan."""

    template_name = "task_list.html"
    context_object_name = "tasks"
    paginate_by = 12

    def get_queryset(self):
        return Task.objects.order_by("-created_at")


class TaskDetailView(LoginRequiredMixin, DetailView):
    """Szczegoly zadania."""

    template_name = "task_detail.html"
    context_object_name = "task"
    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["comments"] = self.object.comments.order_by("created_at")
        context["comment_form"] = CommentForm()
        context["can_edit"] = user.can_manage_work
        context["can_set_status"] = user.can_manage_work or self.object.assigned_to_id == user.id
        context["status_form"] = TaskStatusForm(instance=self.object)
        return context


class ProfileView(LoginRequiredMixin, UpdateView):
    """Profil uzytkownika z avatarem."""

    template_name = "profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("profile-page")
    context_object_name = "profile"

    def get_object(self, queryset=None):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, "Profil został zaktualizowany.")
        return super().form_valid(form)


class WebLoginView(DjangoLoginView):
    """Strona logowania."""

    template_name = "login.html"
    authentication_form = WebAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("dashboard")


class RegisterView(FormView):
    """Strona rejestracji."""

    template_name = "register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            first_name=form.cleaned_data.get("first_name", ""),
            last_name=form.cleaned_data.get("last_name", ""),
            password=form.cleaned_data["password1"],
        )
        login(self.request, user)
        messages.success(self.request, "Konto zostało utworzone.")
        return super().form_valid(form)


# --- CRUD projektow (kierownik / administrator) ---
class ProjectCreateView(ManagerRequiredMixin, CreateView):
    """Tworzenie projektu."""

    model = Project
    form_class = ProjectForm
    template_name = "project_form.html"
    extra_context = {"is_create": True}

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Projekt został utworzony.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project-detail-page", kwargs={"pk": self.object.pk})


class ProjectUpdateView(ManagerRequiredMixin, UpdateView):
    """Edycja projektu."""

    model = Project
    form_class = ProjectForm
    template_name = "project_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Projekt został zaktualizowany.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project-detail-page", kwargs={"pk": self.object.pk})


class ProjectDeleteView(ManagerRequiredMixin, DeleteView):
    """Usuwanie projektu."""

    model = Project
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("project-list-page")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_kind"] = "projekt"
        context["object_label"] = self.object.name
        context["cancel_url"] = reverse("project-detail-page", kwargs={"pk": self.object.pk})
        return context

    def form_valid(self, form):
        messages.success(self.request, "Projekt został usunięty.")
        return super().form_valid(form)


# --- CRUD zadan (kierownik / administrator) ---
class TaskCreateView(ManagerRequiredMixin, CreateView):
    """Tworzenie zadania."""

    model = Task
    form_class = TaskForm
    template_name = "task_form.html"
    extra_context = {"is_create": True}

    def get_initial(self):
        initial = super().get_initial()
        project_id = self.request.GET.get("project")
        if project_id and project_id.isdigit():
            initial["project"] = project_id
        return initial

    def form_valid(self, form):
        messages.success(self.request, "Zadanie zostało utworzone.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("task-detail-page", kwargs={"pk": self.object.pk})


class TaskUpdateView(ManagerRequiredMixin, UpdateView):
    """Edycja zadania."""

    model = Task
    form_class = TaskForm
    template_name = "task_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Zadanie zostało zaktualizowane.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("task-detail-page", kwargs={"pk": self.object.pk})


class TaskDeleteView(ManagerRequiredMixin, DeleteView):
    """Usuwanie zadania."""

    model = Task
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("task-list-page")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_kind"] = "zadanie"
        context["object_label"] = self.object.title
        context["cancel_url"] = reverse("task-detail-page", kwargs={"pk": self.object.pk})
        return context

    def form_valid(self, form):
        messages.success(self.request, "Zadanie zostało usunięte.")
        return super().form_valid(form)


# --- Komentarze i zmiana statusu ---
class TaskCommentCreateView(LoginRequiredMixin, View):
    """Dodanie komentarza do zadania (kazdy zalogowany)."""

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            messages.success(request, "Komentarz został dodany.")
        else:
            messages.error(request, "Komentarz nie może być pusty.")
        return redirect("task-detail-page", pk=task.pk)


class TaskStatusUpdateView(LoginRequiredMixin, View):
    """Szybka zmiana statusu zadania."""

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        can_change = request.user.can_manage_work or task.assigned_to_id == request.user.id
        if not can_change:
            messages.error(request, "Nie masz uprawnień do zmiany statusu.")
            return redirect("task-detail-page", pk=task.pk)
        form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Status zadania został zaktualizowany.")
        else:
            messages.error(request, "Nieprawidłowy status zadania.")
        return redirect("task-detail-page", pk=task.pk)
