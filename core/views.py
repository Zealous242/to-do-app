"""Views for public-facing pages, general layout hubs, and site metadata."""

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Renders the public landing page or redirects authenticated users."""

    template_name = "core/home.html"
