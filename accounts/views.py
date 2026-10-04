"""Views managing user dashboards."""

from typing import Any

from django.views.generic import TemplateView

from task.forms import TaskForm
from task.models import Task
from task.sorting import get_task_sort, sort_tasks, task_sort_choices
from taskgroup.models import TaskGroup


class AccountDashboardView(TemplateView):
    """Render the logged-in user's task dashboard."""

    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Provide the user's tasks and dashboard counts."""
        context = super().get_context_data(**kwargs)

        tasks = Task.objects.filter(
            group__user=self.request.user,
        )

        todo_count = tasks.pending().count()
        completed_count = tasks.completed().count()

        selected_filter = self.request.GET.get("filter", "all")

        if selected_filter == "todo":
            displayed_tasks = tasks.pending()
        elif selected_filter == "completed":
            displayed_tasks = tasks.completed()
        else:
            selected_filter = "all"
            displayed_tasks = tasks

        default_group = TaskGroup.objects.filter(
            user=self.request.user, name="My Tasks"
        ).first()
        form = TaskForm(taskgroup=default_group)
        if default_group is None:
            form.fields["parent"].queryset = Task.objects.none()

        context.update(
            {"form": form},
        )
        sorted_tasks = list(
            sort_tasks(displayed_tasks, self.request.GET.get("sort"))
        )
        context.update(
            {
                "tasks": sorted_tasks,
                "incomplete_tasks": [t for t in sorted_tasks if t.status != "done"],
                "completed_tasks": [t for t in sorted_tasks if t.status == "done"],
                "sort": get_task_sort(self.request.GET.get("sort")),
                "sort_options": task_sort_choices(),
                "todo_count": todo_count,
                "completed_count": completed_count,
                "total_count": todo_count + completed_count,
                "selected_filter": selected_filter,
            }
        )

        return context