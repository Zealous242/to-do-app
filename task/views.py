"""Views for creating, updating, completing, and deleting tasks."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from taskgroup.models import TaskGroup

from .forms import TaskForm
from .models import Task


class UserTaskMixin:
    """Limit task operations to tasks in projects owned by the current user."""

    def get_queryset(self):
        """Return only tasks belonging to the current user's projects."""
        return Task.objects.filter(group__user=self.request.user)


class TaskDetailView(UserTaskMixin, DetailView):
    """Display a task belonging to one of the user's projects."""

    model = Task
    template_name = "task/detail.html"
    context_object_name = "task"


class TaskCreateView(CreateView):
    """Create a task within a project, defaulting to the user's "My Tasks" project."""

    model = Task
    form_class = TaskForm
    template_name = "task/create.html"

    def get_taskgroup(self):
        """Return the requested project, or the default one, owned by the user."""
        if "project_pk" in self.kwargs:
            return get_object_or_404(
                TaskGroup,
                pk=self.kwargs["project_pk"],
                user=self.request.user,
            )
        group, _ = TaskGroup.objects.get_or_create(
            user=self.request.user,
            name="My Tasks",
        )
        return group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["taskgroup"] = self.get_taskgroup()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["taskgroup"] = self.get_taskgroup()
        return kwargs

    def form_valid(self, form):
        form.instance.group = self.get_taskgroup()
        messages.success(self.request, "Task created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("taskgroup:detail", kwargs={"pk": self.object.group_id})


class TaskUpdateView(UserTaskMixin, UpdateView):
    """Edit a task belonging to one of the user's projects."""

    model = Task
    form_class = TaskForm
    template_name = "task/edit.html"
    context_object_name = "task"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["taskgroup"] = self.object.group
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Task updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("taskgroup:detail", kwargs={"pk": self.object.group_id})


class TaskToggleView(View):
    """Toggle a task between pending and completed."""

    def post(self, request, pk):
        """Change the task's completion state."""
        task = get_object_or_404(Task, pk=pk, group__user=request.user)

        if task.status == Task.Status.DONE:
            task.status = Task.Status.TODO
        else:
            task.status = Task.Status.DONE

        task.save(update_fields=["status", "updated_at"])

        return redirect("accounts:dashboard")


class TaskDeleteView(UserTaskMixin, DeleteView):
    """Delete a task belonging to one of the user's projects."""

    model = Task
    template_name = "task/confirm_delete.html"
    context_object_name = "task"

    def form_valid(self, form):
        messages.success(self.request, "Task deleted successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("taskgroup:detail", kwargs={"pk": self.object.group_id})
