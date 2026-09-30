"""Project-level URL configuration."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("core.urls")),
    path("account/", include("accounts.urls")),
    path("auth/", include("allauth.urls")),
    path("task/", include("task.urls")),
    path("project/", include("taskgroup.urls")),
    path("site-admin/", admin.site.urls),
]
