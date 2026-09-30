"""Views for creating, listing, updating, completing, and deleting individual tasks."""

from django.views.generic import TemplateView


class TaskDetailView(TemplateView):
    """Placeholder view for url wiring."""

    template_name = "task/detail.html"
