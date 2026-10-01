"""Define project-level handlers for common HTTP error responses."""

from django.core.exceptions import PermissionDenied
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render

# Centralized error configuration dictionary
ERROR_CONFIG = {
    # URL endpoints MUST use single quotes so as not to break the string in template
    400: {
        "status_code": 400,
        "title": "Bad Request",
        "message": "The request sent to the server was invalid or malformed.",
    },
    403: {
        "status_code": 403,
        "title": "Access Denied",
        "message": "You do not have permission to view this resource.",
    },
    404: {
        "status_code": 404,
        "title": "Page Not Found",
        "message": "The page you are looking for doesn't exist or has been moved.",
    },
    500: {
        "status_code": 500,
        "title": "Server Error",
        "message": "Something went wrong on our server. Please try again later.",
    },
}


# Specific error handlers; status= ensures the response
# uses the appropriate HTTP status code.
def handler400(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Handle HTTP 400 Bad Request responses."""
    return render(request, "error.html", context=ERROR_CONFIG[400], status=400)


def handler403(request: HttpRequest, exception: PermissionDenied) -> HttpResponse:
    """Handle HTTP 403 Forbidden responses."""
    return render(request, "error.html", context=ERROR_CONFIG[403], status=403)


def handler404(request: HttpRequest, exception: Http404) -> HttpResponse:
    """Handle HTTP 404 Page Not Found responses."""
    return render(request, "error.html", context=ERROR_CONFIG[404], status=404)


def handler500(request: HttpRequest) -> HttpResponse:
    """Handle HTTP 500 Server Error responses."""
    # 500 views do not take exception param
    return render(request, "error.html", context=ERROR_CONFIG[500], status=500)
