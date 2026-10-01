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
