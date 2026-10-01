"""Test public pages and unauthenticated user views."""

from django.test import Client
from django.urls import reverse


def test_core_root_url(client: Client) -> None:
    """Check root URL wiring for core module."""
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "core/home.html" in [template.name for template in response.templates]
