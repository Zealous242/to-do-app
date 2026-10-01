"""Views for creating, listing, updating, completing, and deleting individual tasks."""

from django.views.generic import TemplateView, CreateView
from .models import Task
from django.urls import reverse_lazy


class TaskDetailView(TemplateView):
    """Placeholder view for url wiring."""

    template_name = "task/detail.html"


class TaskCreateView(CreateView):
    """Create user tasks."""
    model = Task
    fields = ["title", "description", "due_date", "priority"]
    template_name = "task/create.html"
    success_url = reverse_lazy("accounts:dashboard")
