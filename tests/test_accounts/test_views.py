"""Test the authenticated user's account views."""

from django.test import Client
from django.urls import reverse


def test_accounts_root_url(client: Client) -> None:
    """Check root URL wiring for accounts module."""
    response = client.get(reverse("accounts:dashboard"))

    assert response.status_code == 200
    assert "accounts/dashboard.html" in [template.name for template in response.templates]
