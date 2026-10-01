"""Test the authenticated user's account views."""

import pytest
from django.test import Client
from django.urls import reverse

from accounts.models import User

pytestmark = pytest.mark.django_db


def test_accounts_root_url(client: Client, user: User) -> None:
    """Check root URL wiring for accounts module."""
    client.force_login(user)
    response = client.get(reverse("accounts:dashboard"))

    assert response.status_code == 200
    assert "accounts/dashboard.html" in [
        template.name for template in response.templates
    ]
