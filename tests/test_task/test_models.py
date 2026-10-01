"""Unit tests for the Task model definition, relationships, and validation."""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from task.models import Task
from tests.factories import TaskFactory, TaskGroupFactory


@pytest.mark.django_db
class TestTaskModelAttributesAndDefaults:
    """Test model field defaults, text choices, and string representations."""

    def test_str_returns_title(self) -> None:
        """Test task string representation is its title."""
        task = TaskFactory.build(title="Design Dashboard Component")
        assert str(task) == "Design Dashboard Component"

    def test_default_status_is_todo(self) -> None:
        """Test task status defaults to 'todo'."""
        task = TaskFactory()
        assert task.status == Task.Status.TODO

    def test_status_choices_enum_values(self) -> None:
        """Test task status choices enum values and labels."""
        assert Task.Status.TODO == "todo"
        assert Task.Status.IN_PROGRESS == "in_progress"
        assert Task.Status.DONE == "done"

        assert Task.Status.TODO.label == "To Do"
        assert Task.Status.IN_PROGRESS.label == "In Progress"
        assert Task.Status.DONE.label == "Done"

    def test_priority_choices_enum_values(self) -> None:
        """Test task priority choices enum values and labels."""
        assert Task.Priority.LOW == "L"
        assert Task.Priority.MEDIUM == "M"
        assert Task.Priority.HIGH == "H"
        assert Task.Priority.URGENT == "U"

        assert Task.Priority.LOW.label == "Low"
        assert Task.Priority.URGENT.label == "Urgent"

    def test_timestamps_populate_automatically(self) -> None:
        """Test timestamps auto-populate."""
        task = TaskFactory()
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_meta_default_ordering(self) -> None:
        """Test default ordering of tasks by created_at timestamp."""
        task_1 = TaskFactory(title="Task 1")
        task_2 = TaskFactory(title="Task 2")

        tasks = list(Task.objects.all())
        assert tasks == [task_1, task_2]


@pytest.mark.django_db
class TestTaskModelRelationshipsAndCascades:
    """Test foreign key rules, tree hierarchy, and deletion behavior."""

    def test_task_belongs_to_group(self) -> None:
        """Test task-taskgroup relationship."""
        group = TaskGroupFactory(name="Frontend Refactor")
        task = TaskFactory(group=group)

        assert task.group == group
        assert task in group.tasks.all()

    def test_deleting_group_cascades_to_tasks(self) -> None:
        """Test taskgroup-relationship deletion behaviour."""
        group = TaskGroupFactory()
        task = TaskFactory(group=group)

        group.delete()
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_parent_subtask_relationship(self) -> None:
        """Test subtask-parent relationship."""
        parent_task = TaskFactory(title="Parent Task")
        subtask = TaskFactory(
            parent=parent_task,
            group=parent_task.group,
            title="Subtask",
        )

        assert subtask.parent == parent_task
        assert subtask in parent_task.subtasks.all()

    def test_deleting_parent_cascades_to_subtasks(self) -> None:
        """Test subtask-parent relationship deletion behaviour."""
        parent_task = TaskFactory()
        subtask = TaskFactory(parent=parent_task, group=parent_task.group)

        parent_task.delete()
        assert not Task.objects.filter(pk=subtask.pk).exists()

    def test_null_group_raises_integrity_error(self) -> None:
        """Test task must belong to group."""
        with pytest.raises(IntegrityError):
            Task.objects.create(title="Orphan Task", group=None)


@pytest.mark.django_db
class TestTaskModelValidation:
    """Test model-level business rules and validation logic."""

    def test_prevent_self_as_parent(self) -> None:
        """Test a task cannot be its own parent."""
        task = TaskFactory()
        task.parent = task
        with pytest.raises(ValidationError) as exc_info:
            task.full_clean()

        assert "parent" in exc_info.value.message_dict

    def test_subtask_and_parent_belong_to_same_group(self) -> None:
        """Test business rule consistency across group ownership."""
        group_a = TaskGroupFactory(name="Group A")
        group_b = TaskGroupFactory(name="Group B")

        parent_task = TaskFactory(group=group_a)
        subtask = TaskFactory(group=group_b, parent=parent_task)

        assert subtask.group != parent_task.group
        assert subtask.parent.group == group_a
