"""Management command that fills the database with realistic test data.

Usage examples::

    python manage.py seed_db
    python manage.py seed_db --managers 4 --employees 20 --projects 10 --flush

The command uses the Faker library to generate believable users, projects,
tasks and comments so the application can be demonstrated with non-trivial
content without entering everything by hand.
"""

from __future__ import annotations

import random
from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from apps.comments.models import Comment
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.users.models import User

try:  # pragma: no cover - import guard for a clearer error message
    from faker import Faker
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The 'Faker' package is required for seed_db. Install it with 'pip install Faker'."
    ) from exc


class Command(BaseCommand):
    """Seed the database with fake but realistic project management data."""

    help = "Generate realistic test data (users, projects, tasks, comments) using Faker."

    def add_arguments(self, parser: CommandParser) -> None:
        """Register the command line options."""
        parser.add_argument("--managers", type=int, default=3, help="Number of manager accounts to create.")
        parser.add_argument("--employees", type=int, default=12, help="Number of employee accounts to create.")
        parser.add_argument("--projects", type=int, default=6, help="Number of projects to create.")
        parser.add_argument("--max-tasks", type=int, default=8, help="Maximum number of tasks per project.")
        parser.add_argument("--max-comments", type=int, default=4, help="Maximum number of comments per task.")
        parser.add_argument(
            "--password",
            type=str,
            default="TaskFlow123!",
            help="Password assigned to every generated account.",
        )
        parser.add_argument(
            "--locale",
            type=str,
            default="pl_PL",
            help="Faker locale used to generate the data.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Optional integer seed for reproducible data.",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing non-superuser data before seeding.",
        )

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        """Run the seeding process inside a single transaction."""
        faker = Faker(options["locale"])
        if options["seed"] is not None:
            Faker.seed(options["seed"])
            random.seed(options["seed"])

        if options["flush"]:
            self._flush()

        password = options["password"]
        managers = self._create_users(faker, options["managers"], User.Role.MANAGER, password)
        employees = self._create_users(faker, options["employees"], User.Role.EMPLOYEE, password)

        if not managers:
            self.stderr.write(self.style.ERROR("At least one manager is required to create projects."))
            return

        authors = managers + employees
        projects = self._create_projects(faker, options["projects"], managers)
        tasks = self._create_tasks(faker, projects, employees, options["max_tasks"])
        comments = self._create_comments(faker, tasks, authors, options["max_comments"])

        self.stdout.write(
            self.style.SUCCESS(
                "Seed complete: "
                f"{len(managers)} managers, {len(employees)} employees, "
                f"{len(projects)} projects, {len(tasks)} tasks, {comments} comments."
            )
        )

    def _flush(self) -> None:
        """Remove generated content while keeping superuser accounts."""
        Comment.objects.all().delete()
        Task.objects.all().delete()
        Project.objects.all().delete()
        deleted, _ = User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING(f"Flushed existing data ({deleted} user-related rows removed)."))

    def _create_users(self, faker: Faker, count: int, role: str, password: str) -> list[User]:
        """Create a batch of users with the given role and a populated profile."""
        users: list[User] = []
        for _index in range(count):
            first_name = faker.first_name()
            last_name = faker.last_name()
            username = self._unique_username(faker, first_name, last_name)
            email = f"{username}@example.com"

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
            )

            profile = user.profile
            profile.job_title = faker.job()[:120]
            profile.phone_number = faker.numerify("+48 ### ### ###")
            profile.bio = faker.paragraph(nb_sentences=3)
            profile.save()

            users.append(user)
        return users

    def _unique_username(self, faker: Faker, first_name: str, last_name: str) -> str:
        """Build a unique, slug-like username for a user."""
        base = f"{first_name}.{last_name}".lower()
        base = "".join(ch for ch in base if ch.isalnum() or ch == ".")
        candidate = base or faker.user_name()
        suffix = 1
        username = candidate
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{candidate}{suffix}"
        return username[:150]

    def _create_projects(self, faker: Faker, count: int, managers: list[User]) -> list[Project]:
        """Create projects assigned to random managers."""
        projects: list[Project] = []
        statuses = [choice[0] for choice in Project.Status.choices]
        for _index in range(count):
            start_date = faker.date_between(start_date="-90d", end_date="+10d")
            end_date = start_date + timedelta(days=random.randint(14, 120))
            manager = random.choice(managers)
            project = Project.objects.create(
                name=faker.catch_phrase()[:200],
                description=faker.paragraph(nb_sentences=4),
                start_date=start_date,
                end_date=end_date,
                status=random.choice(statuses),
                manager=manager,
                created_by=manager,
            )
            projects.append(project)
        return projects

    def _create_tasks(
        self,
        faker: Faker,
        projects: list[Project],
        employees: list[User],
        max_tasks: int,
    ) -> list[Task]:
        """Create tasks for each project, optionally assigned to an employee."""
        tasks: list[Task] = []
        statuses = [choice[0] for choice in Task.Status.choices]
        priorities = [choice[0] for choice in Task.Priority.choices]
        for project in projects:
            for _index in range(random.randint(1, max(1, max_tasks))):
                due_date = faker.date_between_dates(date_start=project.start_date, date_end=project.end_date)
                assigned_to = random.choice(employees) if employees and random.random() < 0.8 else None
                task = Task.objects.create(
                    project=project,
                    assigned_to=assigned_to,
                    title=faker.sentence(nb_words=6)[:200],
                    description=faker.paragraph(nb_sentences=3),
                    due_date=due_date,
                    status=random.choice(statuses),
                    priority=random.choice(priorities),
                )
                tasks.append(task)
        return tasks

    def _create_comments(
        self,
        faker: Faker,
        tasks: list[Task],
        authors: list[User],
        max_comments: int,
    ) -> int:
        """Create comments authored by random users on the given tasks."""
        if not authors:
            return 0
        created = 0
        for task in tasks:
            for _index in range(random.randint(0, max(0, max_comments))):
                Comment.objects.create(
                    task=task,
                    author=random.choice(authors),
                    content=faker.paragraph(nb_sentences=2),
                )
                created += 1
        return created
