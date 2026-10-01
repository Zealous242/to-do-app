"""URL routing for public-facing pages such as home, landing, and static views."""

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
]
