"""Project-level utilities for configuration and integration."""

from accounts.models import User


def get_user_display(user: User) -> str:
    """Return the user's display name."""
    return str(user)
