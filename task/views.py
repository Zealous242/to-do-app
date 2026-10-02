"""Views for creating, listing, updating, completing, and deleting individual tasks."""

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
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
    """Create a task within a project owned by the current user."""

    model = Task
    form_class = TaskForm
    template_name = "task/create.html"

    def get_taskgroup(self):
        """Return the requested project only when it belongs to the user."""
        return get_object_or_404(
            TaskGroup,
            pk=self.kwargs["project_pk"],
            user=self.request.user,
        )

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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "taskgroup:detail", kwargs={"pk": self.object.group_id}
        )


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

    def get_success_url(self):
        return reverse_lazy(
            "taskgroup:detail", kwargs={"pk": self.object.group_id}
        )


class TaskDeleteView(UserTaskMixin, DeleteView):
    """Delete a task belonging to one of the user's projects."""

    model = Task
    template_name = "task/confirm_delete.html"
    context_object_name = "task"

    def get_success_url(self):
        return reverse_lazy(
            "taskgroup:detail", kwargs={"pk": self.object.group_id}
        )
