"""Views managing user dashboards."""

from typing import Any

from django.views.generic import TemplateView

from task.models import Task


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

        context.update(
            {
                "tasks": displayed_tasks,
                "todo_count": todo_count,
                "completed_count": completed_count,
                "total_count": todo_count + completed_count,
                "selected_filter": selected_filter,
            }
        )

        return context