"""Zadania Celery dla aplikacji zadan."""

from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.tasks.models import Task, TaskNotification


@shared_task
def send_due_task_reminders():
    """Tworzy przypomnienia dla zadan z terminem w ciagu najblizszych 2 dni."""
    today = timezone.localdate()
    deadline = today + timedelta(days=2)

    tasks = Task.objects.filter(due_date__gte=today, due_date__lt=deadline).exclude(
        status__in=[Task.Status.DONE, Task.Status.CANCELLED]
    )

    created = 0
    for task in tasks:
        recipients = []
        if task.assigned_to_id:
            recipients.append(task.assigned_to)
        if task.project.manager_id and task.project.manager_id != task.assigned_to_id:
            recipients.append(task.project.manager)

        for recipient in recipients:
            message = f"Zadanie '{task.title}' ma termin {task.due_date} i wymaga uwagi."
            notification, was_created = TaskNotification.objects.get_or_create(
                task=task,
                recipient=recipient,
                reminder_date=today,
                defaults={"message": message},
            )
            if was_created:
                created += 1

    return created
