"""Admin configuration for custom users and manager role actions."""

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from .models import User
from .services import RoleChangeError, set_manager_role


@admin.action(description="Make selected users managers")
def make_managers(modeladmin, request, queryset) -> None:
	"""Promote selected non-staff, non-superuser accounts."""
	changed = 0
	for user in queryset:
		try:
			set_manager_role(request.user, user, True)
		except RoleChangeError as error:
			modeladmin.message_user(request, str(error), messages.ERROR)
		else:
			changed += 1
	modeladmin.message_user(request, f"{changed} user(s) made manager.", messages.SUCCESS)


@admin.action(description="Remove manager role from selected users")
def remove_managers(modeladmin, request, queryset) -> None:
	"""Demote selected non-staff, non-superuser accounts."""
	changed = 0
	for user in queryset:
		try:
			set_manager_role(request.user, user, False)
		except RoleChangeError as error:
			modeladmin.message_user(request, str(error), messages.ERROR)
		else:
			changed += 1
	modeladmin.message_user(request, f"{changed} user(s) made regular users.", messages.SUCCESS)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
	"""Expose the application role and shared role actions in admin."""

	fieldsets = (*UserAdmin.fieldsets, ("Application access", {"fields": ("role",)}))
	add_fieldsets = (*UserAdmin.add_fieldsets, ("Application access", {"fields": ("role",)}))
	list_display = (*UserAdmin.list_display, "role")
	list_filter = (*UserAdmin.list_filter, "role")
	actions = [make_managers, remove_managers]
