"""Provide factories for testing."""

from typing import Any

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from task.models import Task
from taskgroup.models import TaskGroup

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances for testing."""

    class Meta:
        model = User
        django_get_or_create = ("username",)

    username: str = factory.Sequence(lambda n: f"user_{n}")
    email: str = factory.LazyAttribute(lambda o: f"{o.username}@example.com")

    @classmethod
    def _create(cls, model_class: type[User], *args: Any, **kwargs: Any) -> User:
        """Use create_user manager method to handle password hashing cleanly."""
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class TaskGroupFactory(DjangoModelFactory):
    """Factory for creating TaskGroup instances for testing."""

    class Meta:
        model = TaskGroup

    user: User = factory.SubFactory(UserFactory)  # type: ignore[assignment]
    name: str = factory.Sequence(lambda n: f"Task Group {n}")


class TaskFactory(DjangoModelFactory):
    """Factory for creating Task instances for testing."""

    class Meta:
        model = Task

    group: TaskGroup = factory.SubFactory(TaskGroupFactory)  # type: ignore[assignment]
    title: str = factory.Sequence(lambda n: f"Task {n}")
    status: str = Task.Status.TODO
    parent: Task | None = None

    @classmethod
    def create(cls, **kwargs: Any) -> Task:
        return super().create(**kwargs)

    @classmethod
    def build(cls, **kwargs: Any) -> Task:
        return super().build(**kwargs)

    @classmethod
    def create_batch(cls, size: int, **kwargs: Any) -> list[Task]:
        return super().create_batch(size, **kwargs)

    @classmethod
    def create_tree(cls, subtask_count: int = 2, **kwargs: Any) -> Task:
        """Helper to create a root task along with N direct child subtasks."""
        root: Task = cls.create(**kwargs)
        cls.create_batch(size=subtask_count, parent=root, group=root.group)
        return root
