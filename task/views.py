"""Views for creating, updating, completing, and deleting tasks."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView

from taskgroup.models import TaskGroup

from .forms import TaskForm
from .models import Task


class UserTaskMixin:
    """Restrict task access to tasks owned by the current user."""

    def get_queryset(self):
        """Return only tasks belonging to the logged-in user."""
        return Task.objects.filter(group__user=self.request.user)


class TaskCreateView(CreateView):
    """Create a task for the logged-in user."""

    model = Task
    form_class = TaskForm
    template_name = "task/create.html"
    success_url = reverse_lazy("accounts:dashboard")

    def form_valid(self, form):
        """Assign the task to the user's default task group."""
        group, _ = TaskGroup.objects.get_or_create(
            user=self.request.user,
            name="My Tasks",
        )

        form.instance.group = group

        messages.success(self.request, "Task created successfully.")

        return super().form_valid(form)


class TaskUpdateView(UserTaskMixin, UpdateView):
    """Update one of the logged-in user's tasks."""

    model = Task
    form_class = TaskForm
    template_name = "task/edit.html"
    success_url = reverse_lazy("accounts:dashboard")

    def form_valid(self, form):
        """Display confirmation after updating."""
        messages.success(self.request, "Task updated successfully.")
        return super().form_valid(form)


class TaskToggleView(View):
    """Toggle a task between pending and completed."""

    def post(self, request, pk):
        """Change the task's completion state."""
        task = get_object_or_404(
            Task,
            pk=pk,
            group__user=request.user,
        )

        if task.status == Task.Status.DONE:
            task.status = Task.Status.TODO
        else:
            task.status = Task.Status.DONE

        task.save(update_fields=["status", "updated_at"])

        return redirect("accounts:dashboard")


class TaskDeleteView(View):
    """Delete one of the logged-in user's tasks."""

    def post(self, request, pk):
        """Delete the requested task."""
        task = get_object_or_404(
            Task,
            pk=pk,
            group__user=request.user,
        )

        task.delete()

        messages.success(request, "Task deleted successfully.")

        return redirect("accounts:dashboard")