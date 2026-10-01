"""Unit tests for TaskQuerySet custom methods."""

from typing import Any

import pytest

from task.models import Task
from tests.factories import TaskFactory


@pytest.mark.django_db
class TestTaskQuerySetFilters:
    """Test filtering helper methods on TaskQuerySet."""

    def test_completed(self, task_tree: dict[str, Task]) -> None:
        """Test completed() returns only tasks with status 'done'."""
        completed_tasks = Task.objects.completed()

        assert completed_tasks.count() == 2
        assert set(completed_tasks) == {
            task_tree["root_2"],
            task_tree["subtask_1_1"],
        }

    def test_pending(self, task_tree: dict[str, Task]) -> None:
        """Test pending() returns only tasks with status 'todo' or 'in_progress'."""
        pending_tasks = Task.objects.pending()

        assert pending_tasks.count() == 2
        assert set(pending_tasks) == {
            task_tree["root_1"],
            task_tree["subtask_1_2"],
        }

    def test_top_level(self, task_tree: dict[str, Task]) -> None:
        """Test top_level() returns only tasks with no parent."""
        root_tasks = Task.objects.top_level()

        assert root_tasks.count() == 2
        assert set(root_tasks) == {
            task_tree["root_1"],
            task_tree["root_2"],
        }

    def test_subtasks(self, task_tree: dict[str, Task]) -> None:
        """Test subtasks() returns only tasks with a parent."""
        child_tasks = Task.objects.subtasks()

        assert child_tasks.count() == 2
        assert set(child_tasks) == {
            task_tree["subtask_1_1"],
            task_tree["subtask_1_2"],
        }

    def test_queryset_chaining(self, task_tree: dict[str, Task]) -> None:
        """Test queryset helper methods chain correctly."""
        pending_roots = Task.objects.top_level().pending()

        assert pending_roots.count() == 1
        assert pending_roots.first() == task_tree["root_1"]


@pytest.mark.django_db
class TestTaskQuerySetOptimizations:
    """Test prefetching and query optimization methods."""

    def test_with_prefetched_children(
        self, django_assert_num_queries: Any, task_tree: dict[str, Task]
    ) -> None:
        """Test prefetching child tasks."""
        # Query 1: Top-level tasks
        # Query 2: Prefetched child subtasks
        with django_assert_num_queries(2):
            roots = list(Task.objects.top_level().with_prefetched_children())

            child_titles = [
                [child.title for child in root.subtasks.all()] for root in roots
            ]

        assert len(child_titles) == 2

    def test_with_deep_tree(
        self, django_assert_num_queries: Any, task_tree: dict[str, Task]
    ) -> None:
        """Test prefetching a deep tree of tasks."""
        # Query 1: Main task query with group & parent JOINed (select_related)
        # Query 2: Prefetched direct subtasks
        # Query 3: Prefetched 2nd-level subtasks
        with django_assert_num_queries(3):
            tasks = list(Task.objects.with_deep_tree(depth=2))

            for task in tasks:
                # Accessing foreign keys should hit cache
                _ = task.group.name
                if task.parent:
                    _ = task.parent.title

                # Accessing subtasks should hit cache
                _ = list(task.subtasks.all())

    def test_create_tree_factory_helper(self) -> None:
        """Test the custom create_tree factory classmethod."""
        root = TaskFactory.create_tree(subtask_count=3, title="Branch Root")

        assert root.subtasks.count() == 3
        assert all(child.group == root.group for child in root.subtasks.all())
