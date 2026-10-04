"""Shared sorting options for task lists."""

from django.db.models import QuerySet
from django.db.models.functions import Lower

TASK_SORT_OPTIONS = {
    "created": ("Oldest first", ("created_at", "pk")),
    "-created": ("Newest first", ("-created_at", "-pk")),
    "name": ("Name (A-Z)", (Lower("title"), "pk")),
    "-name": ("Name (Z-A)", (Lower("title").desc(), "-pk")),
}
DEFAULT_TASK_SORT = "created"


def get_task_sort(value: str | None) -> str:
    """Return a valid sort key, falling back to the default."""
    return value if value in TASK_SORT_OPTIONS else DEFAULT_TASK_SORT


def sort_tasks(tasks: QuerySet, value: str | None) -> QuerySet:
    """Order a task queryset by the requested sort key."""
    return tasks.order_by(*TASK_SORT_OPTIONS[get_task_sort(value)][1])


def task_sort_choices() -> list[tuple[str, str]]:
    """Return (key, label) pairs for rendering a sort dropdown."""
    return [(key, label) for key, (label, _) in TASK_SORT_OPTIONS.items()]