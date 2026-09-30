"""Data models for individual tasks, priorities and completion states."""

from typing import Self

from django.core.exceptions import ValidationError
from django.db import models

from taskgroup.models import TaskGroup


class TaskQuerySet(models.QuerySet):
    """Provide efficient helper methods for common queries."""

    def completed(self) -> Self:
        """Return tasks with Status.DONE."""
        return self.filter(status="done")

    def pending(self) -> Self:
        """Return tasks with Status.IN_PROGRESS and Status.TOD."""
        return self.exclude(status="done")

    def top_level(self) -> Self:
        """Return root tasks (tasks without a parent)."""
        return self.filter(parent__isnull=True)

    def subtasks(self) -> Self:
        """Return only child tasks (tasks with a parent)."""
        return self.filter(parent__isnull=False)

    def with_prefetched_children(self) -> Self:
        """Prefetch direct child subtasks."""
        return self.prefetch_related("subtasks")

    def with_deep_tree(self, depth: int = 2) -> Self:
        """Prefetch nested subtasks up to a specified depth."""
        lookups = ["subtasks" + "__subtasks" * i for i in range(depth)]
        return self.select_related("group", "parent").prefetch_related(*lookups)


class Task(models.Model):
    """An individual task, with support for task hierarchy."""

    class Priority(models.TextChoices):
        LOW = "L", "Low"
        MEDIUM = "M", "Medium"
        HIGH = "H", "High"
        URGENT = "U", "Urgent"

    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"

    group = models.ForeignKey(
        TaskGroup,
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text="The group or project this task belongs to.",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subtasks",
        help_text="Parent task for hierarchical relationships.",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )
    priority = models.CharField(
        max_length=1,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TaskQuerySet.as_manager()

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self) -> str:
        """Return task title as identifier."""
        return self.title

    def clean(self) -> None:
        """Validate model constraints prior to saving."""
        super().clean()
        if self.parent_id and self.parent_id == self.pk:
            raise ValidationError({"parent": "A task cannot be its own parent."})
