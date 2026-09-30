"""Views for public-facing pages, general layout hubs, and site metadata."""

from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from global_login_required import login_not_required


@method_decorator(login_not_required, name="dispatch")
class HomeView(TemplateView):
    """Renders the public landing page or redirects authenticated users."""

    template_name = "core/home.html"
