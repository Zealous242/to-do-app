"""Shared account-role and manager-access rules."""

from django.core.exceptions import PermissionDenied
from django.db import transaction

from .models import User


class RoleChangeError(Exception):
    """Raised when a manager role change violates an application rule."""


def is_manager(user: User) -> bool:
    """Return whether a user can access the management area."""
    return bool(
        user.is_authenticated
        and (user.is_superuser or user.role == User.Role.MANAGER)
    )


def can_change_roles(user: User) -> bool:
    """Return whether a dashboard manager or admin may change roles."""
    return is_manager(user) or bool(user.is_staff)


def manageable_users():
    """Return users that application managers may view and change."""
    return User.objects.filter(is_superuser=False, is_staff=False)


@transaction.atomic
def set_manager_role(actor: User, target: User, make_manager: bool) -> User:
    """Apply a manager role change after enforcing shared safety rules."""
    if not can_change_roles(actor):
        raise PermissionDenied

    if target.is_superuser or target.is_staff:
        raise RoleChangeError("Staff and superuser accounts cannot be changed here.")

    if not make_manager and target.pk == actor.pk:
        raise RoleChangeError("You cannot remove manager access from your own account.")

    if not make_manager and target.role == User.Role.MANAGER:
        manager_count = User.objects.filter(
            role=User.Role.MANAGER,
            is_active=True,
            is_superuser=False,
        ).count()
        if manager_count <= 1 and not User.objects.filter(
            is_superuser=True,
            is_active=True,
        ).exists():
            raise RoleChangeError("The system must keep at least one manager.")

    target.role = User.Role.MANAGER if make_manager else User.Role.USER
    target.save(update_fields=["role"])
    return target


@transaction.atomic
def set_user_active(actor: User, target: User, active: bool) -> User:
    """Activate or deactivate a manageable account."""
    if not is_manager(actor):
        raise PermissionDenied

    if target.is_superuser or target.is_staff:
        raise RoleChangeError("Staff and superuser accounts cannot be changed here.")

    if target.pk == actor.pk:
        raise RoleChangeError("You cannot change your own account here.")

    if not active and target.role == User.Role.MANAGER:
        active_manager_count = User.objects.filter(
            role=User.Role.MANAGER,
            is_active=True,
            is_superuser=False,
        ).count()
        if active_manager_count <= 1 and not User.objects.filter(
            is_superuser=True,
            is_active=True,
        ).exists():
            raise RoleChangeError("The system must keep at least one active manager.")

    target.is_active = active
    target.save(update_fields=["is_active"])
    return target