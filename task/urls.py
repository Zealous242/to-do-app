"""URL routing for task management."""

from django.urls import path

from . import views

app_name = "task"

urlpatterns = [
    path("create/", views.TaskCreateView.as_view(), name="create"),
    path("project/<int:project_pk>/create/", views.TaskCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.TaskUpdateView.as_view(), name="edit"),
    path("<int:pk>/toggle/", views.TaskToggleView.as_view(), name="toggle"),
    path("<int:pk>/delete/", views.TaskDeleteView.as_view(), name="delete"),
    path("<int:pk>/", views.TaskDetailView.as_view(), name="detail"),
]
