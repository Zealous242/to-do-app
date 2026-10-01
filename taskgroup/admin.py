"""Admin interface for managing task groups (projects) and member access."""

from django.contrib import admin

from .models import TaskGroup

admin.site.register(TaskGroup)
