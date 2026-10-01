"""Admin interfaces and filtering for task management and status updates."""

from django.contrib import admin

from .models import Task

admin.site.register(Task)
