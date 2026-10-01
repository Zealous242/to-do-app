"""Provide fixtures for tests."""

import pytest
from pytest_factoryboy import register

from accounts.models import User
from task.models import Task
from taskgroup.models import TaskGroup

from .factories import TaskFactory, TaskGroupFactory

register(TaskFactory)
register(TaskGroupFactory)


@pytest.fixture
def user(db: None) -> User:
    """Fixture providing a user for tests."""
    user = User(username="brian_of_nazareth", email="brian@brightside.org")
    user.set_unusable_password()
    user.save()
    return user


@pytest.fixture
def staff_user(db: None) -> User:
    """Fixture providing a staff user for tests."""
    return User.objects.create_user(
        username="king_arthur",
        email="arthur@camelot.gov",
        password="spam-spam-spam-eggs",
        is_staff=True,
    )


@pytest.fixture
def taskgroup(db: None, user: User) -> TaskGroup:
    """Fixture providing a taskgroup for tests."""
    return TaskGroupFactory(user=user, name="Project")


@pytest.fixture
def task(db: None, taskgroup: TaskGroup) -> Task:
    """Fixture providing a task for tests."""
    task = TaskFactory(title="Write Unit Tests", group=taskgroup)
    return task


@pytest.fixture
def task_tree(db: None) -> dict[str, Task]:
    """Fixture providing a task tree for tests."""
    group = TaskGroupFactory(name="Test Group")

    root_1 = TaskFactory(
        group=group,
        title="Root 1",
        status=Task.Status.TODO,
    )
    root_2 = TaskFactory(
        group=group,
        title="Root 2",
        status=Task.Status.DONE,
    )
    subtask_1_1 = TaskFactory(
        group=group,
        parent=root_1,
        title="Subtask 1.1",
        status=Task.Status.DONE,
    )
    subtask_1_2 = TaskFactory(
        group=group,
        parent=root_1,
        title="Subtask 1.2",
        status=Task.Status.IN_PROGRESS,
    )

    return {
        "root_1": root_1,
        "root_2": root_2,
        "subtask_1_1": subtask_1_1,
        "subtask_1_2": subtask_1_2,
    }
