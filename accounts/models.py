"""Custom User models, user profiles, and role-based access control structures."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Minimal extension of AbstractUser to meet Chameleon's user model needs."""

    email = models.EmailField(unique=True)

    def __str__(self) -> str:
        """Return the user's display name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email
