"""URL routing for manager authentication and user management."""

from django.urls import path

from . import manager_views

app_name = "manage"

urlpatterns = [
    path("login/", manager_views.ManagerLoginView.as_view(), name="login"),
    path("", manager_views.ManagerDashboardView.as_view(), name="dashboard"),
    path(
        "users/<int:pk>/",
        manager_views.ManagerUserDetailView.as_view(),
        name="user-detail",
    ),
    path(
        "users/<int:pk>/edit/",
        manager_views.ManagerUserUpdateView.as_view(),
        name="user-edit",
    ),
    path(
        "users/<int:pk>/password/",
        manager_views.ManagerPasswordView.as_view(),
        name="user-password",
    ),
    path(
        "users/<int:pk>/role/",
        manager_views.ManagerRoleView.as_view(),
        name="user-role",
    ),
    path(
        "users/<int:pk>/active/",
        manager_views.ManagerActiveView.as_view(),
        name="user-active",
    ),
]