"""URL routing for task group navigation, project dashboards, and group management."""

from django.urls import path

from . import views

app_name = "taskgroup"

urlpatterns = [
    path("<int:pk>/", views.TaskGroupDetailView.as_view(), name="detail"),
]