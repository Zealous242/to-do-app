"""Test views for managing groups of tasks."""

from django.test import Client
from django.urls import reverse


def test_taskgroup_url_wiring(client: Client) -> None:
    """Check URL wiring for taskgroup module."""
    response = client.get(reverse("taskgroup:detail"))

    assert response.status_code == 200
    assert "taskgroup/detail.html" in [template.name for template in response.templates]
