"""URL routing for task group navigation, project dashboards, and group management."""

from django.urls import path

from . import views

app_name = "taskgroup"

urlpatterns = [
    path("", views.TaskGroupListView.as_view(), name="list"),
    path("<int:pk>/edit/", views.TaskGroupUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.TaskGroupDeleteView.as_view(), name="delete"),
    path("<int:pk>/", views.TaskGroupDetailView.as_view(), name="detail"),
]
