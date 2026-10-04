"""Views for managing task group dashboards, organizing tasks, and project workflows."""

from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

from task.forms import TaskForm
from task.sorting import get_task_sort, sort_tasks, task_sort_choices

from .forms import TaskGroupForm
from .models import TaskGroup


class UserTaskGroupMixin:
    """Limit task-group operations to projects owned by the current user."""

    def get_queryset(self):
        """Return only task groups owned by the current user."""
        return TaskGroup.objects.filter(user=self.request.user)


class TaskGroupListView(ListView):
    """Display the task groups owned by the logged-in user."""

    model = TaskGroup
    template_name = "taskgroup/list.html"
    context_object_name = "taskgroups"
    form_class = TaskGroupForm

    SORT_OPTIONS = {
        "name": ("Name (A-Z)", (Lower("name"), "pk")),
        "-name": ("Name (Z-A)", (Lower("name").desc(), "-pk")),
        "-created": ("Newest first", ("-created_at", "-pk")),
        "created": ("Oldest first", ("created_at", "pk")),
    }
    default_sort = "name"

    def get_sort(self) -> str:
        """Return the requested sort key, falling back to the default."""
        sort = self.request.GET.get("sort", self.default_sort)
        return sort if sort in self.SORT_OPTIONS else self.default_sort

    def get_queryset(self):
        """Limit the list to the user's task groups, ordered by the chosen sort."""
        ordering = self.SORT_OPTIONS[self.get_sort()][1]
        return super().get_queryset().filter(user=self.request.user).order_by(*ordering)

    def get_context_data(self, **kwargs):
        """Add the project form and sort options to the list page context."""
        context = super().get_context_data(**kwargs)
        context["sort"] = self.get_sort()
        context["sort_options"] = [(key, label) for key, (label, _) in self.SORT_OPTIONS.items()]
        context.setdefault("form", self.form_class())
        return context

    def post(self, request, *args, **kwargs) -> HttpResponse:
        """Create a project for the logged-in user from the list page."""
        self.object_list = self.get_queryset()
        form = self.form_class(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect(request.get_full_path())

        return self.render_to_response(self.get_context_data(form=form), status=400)


class TaskGroupUpdateView(UserTaskGroupMixin, UpdateView):
    """Allow a user to edit one of their projects."""

    model = TaskGroup
    form_class = TaskGroupForm
    template_name = "taskgroup/edit.html"
    context_object_name = "taskgroup"
    success_url = reverse_lazy("taskgroup:list")


class TaskGroupDeleteView(UserTaskGroupMixin, DeleteView):
    """Allow a user to delete one of their projects."""

    model = TaskGroup
    template_name = "taskgroup/confirm_delete.html"
    context_object_name = "taskgroup"
    success_url = reverse_lazy("taskgroup:list")


class TaskGroupDetailView(UserTaskGroupMixin, DetailView):
    """Display a project and its tasks for the current user."""

    model = TaskGroup
    template_name = "taskgroup/detail.html"
    context_object_name = "taskgroup"

    def get_context_data(self, **kwargs):
        """Add a blank task form for the create-task modal."""
        context = super().get_context_data(**kwargs)
        context["form"] = TaskForm(taskgroup=self.object)
        sort = self.request.GET.get("sort")
        tasks = list(sort_tasks(self.object.tasks.all(), sort))
        context["tasks"] = tasks
        context["incomplete_tasks"] = [t for t in tasks if t.status != "done"]
        context["completed_tasks"] = [t for t in tasks if t.status == "done"]
        context["sort"] = get_task_sort(sort)
        context["sort_options"] = task_sort_choices()
        return context


# class TaskGroupDetailView(DetailView):
#     """Displays details and associated tasks for a specific task group."""

#     model = TaskGroup
#     template_name = "taskgroups/taskgroup_detail.html"
#     context_object_name = "taskgroup"

#     def get_queryset(self):
#         return TaskGroup.objects.filter(owner=self.request.user)
