"""URL routing for task management, status toggles, filtering, and detail views."""

from django.urls import path

from . import views

app_name = "task"

urlpatterns = [
    path("<int:pk>/", views.TaskDetailView.as_view(), name="detail"),
]
