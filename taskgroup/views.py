"""Views for managing task group dashboards, organizing tasks, and project workflows."""

from django.views.generic import TemplateView


class TaskGroupDetailView(TemplateView):
    """Placeholder view for url wiring."""

    template_name = "taskgroup/detail.html"


# class TaskGroupDetailView(DetailView):
#     """Displays details and associated tasks for a specific task group."""

#     model = TaskGroup
#     template_name = "taskgroups/taskgroup_detail.html"
#     context_object_name = "taskgroup"

#     def get_queryset(self):
#         return TaskGroup.objects.filter(owner=self.request.user)
