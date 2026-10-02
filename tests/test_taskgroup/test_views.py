"""Test views for managing groups of tasks."""

import pytest
from django.test import Client
from django.urls import reverse

from accounts.models import User
from taskgroup.models import TaskGroup

pytestmark = pytest.mark.django_db


def test_taskgroup_url_wiring(client: Client, user: User, taskgroup: TaskGroup) -> None:
    """Check URL wiring for taskgroup module."""
    client.force_login(user)
    response = client.get(reverse("taskgroup:detail", kwargs={"pk": taskgroup.pk}))

    assert response.status_code == 200
    assert "taskgroup/detail.html" in [template.name for template in response.templates]


def test_taskgroup_list_shows_only_current_users_groups(
    client: Client, user: User, taskgroup: TaskGroup
) -> None:
    """Show the logged-in user's task groups and hide other users' groups."""
    other_group = TaskGroup.objects.create(
        user=User.objects.create_user("other"), name="Other"
    )
    client.force_login(user)

    response = client.get(reverse("taskgroup:list"))

    assert response.status_code == 200
    assert list(response.context["taskgroups"]) == [taskgroup]
    assert taskgroup.name in response.content.decode()
    assert other_group.name not in response.content.decode()


def test_taskgroup_list_requires_login(client: Client) -> None:
    """Redirect anonymous users to the login page."""
    response = client.get(reverse("taskgroup:list"))

    assert response.status_code == 302
    assert response.url.startswith("/auth/login/")


def test_user_can_create_taskgroup_from_list_page(client: Client, user: User) -> None:
    """Create a project and assign it to the logged-in user."""
    client.force_login(user)

    response = client.post(
        reverse("taskgroup:list"),
        {"name": "Website launch", "description": "Prepare the release."},
    )

    assert response.status_code == 200
    project = TaskGroup.objects.get(name="Website launch")
    assert project.user == user
    assert project.description == "Prepare the release."
    assert project.name in response.content.decode()


def test_taskgroup_creation_requires_a_name(client: Client, user: User) -> None:
    """Keep the project form on the page when validation fails."""
    client.force_login(user)

    response = client.post(reverse("taskgroup:list"), {"name": ""})

    assert response.status_code == 400
    assert TaskGroup.objects.count() == 0
    assert "This field is required" in response.content.decode()


def test_user_can_edit_owned_taskgroup(client: Client, user: User, taskgroup: TaskGroup) -> None:
    """Update an owned project's name and description."""
    client.force_login(user)

    response = client.post(
        reverse("taskgroup:edit", kwargs={"pk": taskgroup.pk}),
        {"name": "Renamed project", "description": "Updated details."},
    )

    assert response.status_code == 302
    assert response.url == reverse("taskgroup:list")
    taskgroup.refresh_from_db()
    assert taskgroup.name == "Renamed project"
    assert taskgroup.description == "Updated details."


def test_user_cannot_edit_another_users_taskgroup(
    client: Client, user: User, taskgroup: TaskGroup
) -> None:
    """Prevent editing a project owned by another user."""
    other_user = User.objects.create_user("other")
    taskgroup.user = other_user
    taskgroup.save()
    client.force_login(user)

    response = client.get(reverse("taskgroup:edit", kwargs={"pk": taskgroup.pk}))

    assert response.status_code == 404


def test_user_can_delete_owned_taskgroup(client: Client, user: User, taskgroup: TaskGroup) -> None:
    """Delete an owned project after confirmation."""
    client.force_login(user)

    response = client.post(reverse("taskgroup:delete", kwargs={"pk": taskgroup.pk}))

    assert response.status_code == 302
    assert response.url == reverse("taskgroup:list")
    assert not TaskGroup.objects.filter(pk=taskgroup.pk).exists()


def test_user_cannot_delete_another_users_taskgroup(
    client: Client, user: User, taskgroup: TaskGroup
) -> None:
    """Prevent deleting a project owned by another user."""
    other_user = User.objects.create_user("other")
    taskgroup.user = other_user
    taskgroup.save()
    client.force_login(user)

    response = client.post(reverse("taskgroup:delete", kwargs={"pk": taskgroup.pk}))

    assert response.status_code == 404
    assert TaskGroup.objects.filter(pk=taskgroup.pk).exists()
