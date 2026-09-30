"""Test views for managing individual tasks."""

from django.test import Client
from django.urls import reverse


def test_task_url_wiring(client: Client) -> None:
    """Check URL wiring for task module."""
    response = client.get(reverse("task:detail"))

    assert response.status_code == 200
    assert "task/detail.html" in [template.name for template in response.templates]
