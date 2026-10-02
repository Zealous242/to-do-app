"""Test views for managing individual tasks."""

import pytest
from django.test import Client
from django.urls import reverse

from accounts.models import User
from task.models import Task
from taskgroup.models import TaskGroup

pytestmark = pytest.mark.django_db


def test_task_url_wiring(client: Client, user: User, task: Task) -> None:
    """Check URL wiring for task module."""
    client.force_login(user)
    response = client.get(reverse("task:detail", kwargs={"pk": task.pk}))

    assert response.status_code == 200
    assert "task/detail.html" in [template.name for template in response.templates]


def test_user_can_create_task_in_owned_project(
    client: Client, user: User, taskgroup: TaskGroup
) -> None:
    """Create a task and assign it to the selected project."""
    client.force_login(user)

    response = client.post(
        reverse("task:create", kwargs={"project_pk": taskgroup.pk}),
        {
            "title": "Write documentation",
            "status": Task.Status.TODO,
            "description": "Document the workflow.",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("taskgroup:detail", kwargs={"pk": taskgroup.pk})
    created_task = Task.objects.get(title="Write documentation")
    assert created_task.group == taskgroup


def test_user_cannot_create_task_in_another_users_project(
    client: Client, user: User, taskgroup: TaskGroup
) -> None:
    """Prevent creating a task in a project owned by another user."""
    other_user = User.objects.create_user("other")
    taskgroup.user = other_user
    taskgroup.save()
    client.force_login(user)

    response = client.get(reverse("task:create", kwargs={"project_pk": taskgroup.pk}))

    assert response.status_code == 404


def test_user_can_edit_owned_task(client: Client, user: User, task: Task) -> None:
    """Update an owned task."""
    client.force_login(user)

    response = client.post(
        reverse("task:edit", kwargs={"pk": task.pk}),
        {
            "title": "Updated task",
            "status": Task.Status.DONE,
            "description": "Finished work.",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("taskgroup:detail", kwargs={"pk": task.group_id})
    task.refresh_from_db()
    assert task.title == "Updated task"
    assert task.status == Task.Status.DONE


def test_user_cannot_edit_another_users_task(
    client: Client, user: User, task: Task
) -> None:
    """Prevent editing a task in another user's project."""
    other_user = User.objects.create_user("other")
    task.group.user = other_user
    task.group.save()
    client.force_login(user)

    response = client.get(reverse("task:edit", kwargs={"pk": task.pk}))

    assert response.status_code == 404


def test_user_can_delete_owned_task(client: Client, user: User, task: Task) -> None:
    """Delete an owned task after confirmation."""
    client.force_login(user)

    response = client.post(reverse("task:delete", kwargs={"pk": task.pk}))

    assert response.status_code == 302
    assert response.url == reverse("taskgroup:detail", kwargs={"pk": task.group_id})
    assert not Task.objects.filter(pk=task.pk).exists()


def test_user_cannot_delete_another_users_task(
    client: Client, user: User, task: Task
) -> None:
    """Prevent deleting a task in another user's project."""
    other_user = User.objects.create_user("other")
    task.group.user = other_user
    task.group.save()
    client.force_login(user)

    response = client.post(reverse("task:delete", kwargs={"pk": task.pk}))

    assert response.status_code == 404
    assert Task.objects.filter(pk=task.pk).exists()
