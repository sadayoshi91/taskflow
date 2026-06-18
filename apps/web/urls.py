"""URL routes for the TaskFlow web frontend."""

from __future__ import annotations

from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.web.views import (
    DashboardView,
    ProfileView,
    ProjectCreateView,
    ProjectDeleteView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
    RegisterView,
    TaskCommentCreateView,
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskStatusUpdateView,
    TaskUpdateView,
    WebLoginView,
)

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # Projects
    path("projects/", ProjectListView.as_view(), name="project-list-page"),
    path("projects/new/", ProjectCreateView.as_view(), name="project-create-page"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail-page"),
    path("projects/<int:pk>/edit/", ProjectUpdateView.as_view(), name="project-update-page"),
    path("projects/<int:pk>/delete/", ProjectDeleteView.as_view(), name="project-delete-page"),
    # Tasks
    path("tasks/", TaskListView.as_view(), name="task-list-page"),
    path("tasks/new/", TaskCreateView.as_view(), name="task-create-page"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail-page"),
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="task-update-page"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete-page"),
    path("tasks/<int:pk>/comment/", TaskCommentCreateView.as_view(), name="task-comment-page"),
    path("tasks/<int:pk>/status/", TaskStatusUpdateView.as_view(), name="task-status-page"),
    # Account
    path("profile/", ProfileView.as_view(), name="profile-page"),
    path("login/", WebLoginView.as_view(), name="web-login"),
    path("register/", RegisterView.as_view(), name="web-register"),
    path("logout/", LogoutView.as_view(next_page="web-login"), name="web-logout"),
]
