"""Project-level URL configuration."""

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView


urlpatterns = [
    path("", include("core.urls")),
    path("account/", include("accounts.urls")),
    path("auth/", include("allauth.urls")),
    path("task/", include("task.urls")),
    path("project/", include("taskgroup.urls")),
    path("site-admin/", admin.site.urls),
    # Redirect browsers who request favicon.ico at root
    path("favicon.ico", RedirectView.as_view(url="/static/favicon/favicon.ico", permanent=True)),
]


handler400 = "main.error_handlers.handler400"
handler403 = "main.error_handlers.handler403"
handler404 = "main.error_handlers.handler404"
handler500 = "main.error_handlers.handler500"
