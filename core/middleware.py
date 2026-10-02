"""Custom middleware for Chameleon."""

from collections.abc import Callable

from django.contrib import messages
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.template.loader import render_to_string

# Define type alias for Django responses
DjangoResponse = HttpResponse | StreamingHttpResponse


class HtmxMessageMiddleware:
    """Middleware to handle message rendering with HTMX.

    Intercepts HTMX HTML responses and appends pending messages
    via Out-of-Band(OOB) swapping, allowing standard Django messages
    to be rendered with HTMX without full page reloads.
    """

    def __init__(self, get_response: Callable[[HttpRequest], DjangoResponse]) -> None:
        """Initialize the middleware instance.

        Args:
            get_response: The next middleware or view callable in the Django
                request/response chain.

        Returns: None
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> DjangoResponse:
        """Process incoming requests and modify HTMX responses.

        Checks if the request originated from HTMX and returned HTML. If pending
        Django messages exist, renders them into an OOB container snippet and
        appends the payload to the response content. Converts HTTP 204 (No Content)
        responses to HTTP 200 to allow HTMX to execute the OOB swap.

        Args:
            request: The incoming Django HTTP request instance.

        Returns:
            The original or modified Django HTTP response instance containing
            OOB message markup if messages were present.
        """
        response = self.get_response(request)

        # Process when it's an HTMX request returning HTML
        content_type = response.get("Content-Type", "")
        is_html = "text/html" in content_type

        # Allow success and client error statuses (e.g., 400 validation errors)
        if request.htmx and is_html and response.status_code < 500:
            current_messages = messages.get_messages(request)
            if current_messages:
                # Render the OOB payload wrapper
                oob_html = render_to_string(
                    "shared/shell/messages.html",
                    {
                        "messages": current_messages,
                        "hx_oob": True,
                    },
                    request=request,
                )

                # Handle HTTP 204 (No Content)
                if response.status_code == 204:
                    response.status_code = 200
                    response["Content-Type"] = "text/html; charset=utf-8"
                    response.content = oob_html.encode("utf-8")
                # Append OOB HTML to standard HTTP responses
                elif isinstance(response, HttpResponse):
                    response.content += oob_html.encode("utf-8")

        return response
