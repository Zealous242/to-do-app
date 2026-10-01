"""Test views for managing individual tasks."""

import pytest
from django.test import Client
from django.urls import reverse

from accounts.models import User
from task.models import Task

pytestmark = pytest.mark.django_db


def test_task_url_wiring(client: Client, user: User, task: Task) -> None:
    """Check URL wiring for task module."""
    client.force_login(user)
    response = client.get(reverse("task:detail", kwargs={"pk": task.pk}))

    assert response.status_code == 200
    assert "task/detail.html" in [template.name for template in response.templates]
