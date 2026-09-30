"""URL routing for authentication, registration, password resets, and user profiles."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.AccountDashboardView.as_view(), name="dashboard"),
]
