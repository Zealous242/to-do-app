"""Data models for task groups (projects), group ownership, and task organization."""

from django.conf import settings
from django.db import models


class TaskGroup(models.Model):
    """Group related tasks together (e.g., Projects, Modules, or Epics)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="taskgroups",
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
