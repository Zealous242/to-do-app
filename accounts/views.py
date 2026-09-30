"""Views managing user registration, authentication, profile management, and roles."""

from typing import Any

from django.views.generic import TemplateView


class AccountDashboardView(TemplateView):
    """Render the user's account dashboard."""

    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Retrieve the user's most recently created data."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        return context
