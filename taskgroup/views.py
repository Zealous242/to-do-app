"""Views for managing task group dashboards, organizing tasks, and project workflows."""

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

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

    def get_queryset(self):
        """Limit the list to task groups owned by the current user."""
        return super().get_queryset().filter(user=self.request.user).order_by("name")

    def get_context_data(self, **kwargs):
        """Add the project form to the list page context."""
        context = super().get_context_data(**kwargs)
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
            return self.render_to_response(self.get_context_data())

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


# class TaskGroupDetailView(DetailView):
#     """Displays details and associated tasks for a specific task group."""

#     model = TaskGroup
#     template_name = "taskgroups/taskgroup_detail.html"
#     context_object_name = "taskgroup"

#     def get_queryset(self):
#         return TaskGroup.objects.filter(owner=self.request.user)
