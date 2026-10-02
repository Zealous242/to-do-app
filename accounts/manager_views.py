"""Views for manager authentication and user administration."""

from datetime import timedelta
from typing import Any

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import DetailView, FormView, ListView, UpdateView

from task.models import Task

from .forms import ManagerLoginForm, ManagerPasswordForm, ManagerUserForm
from .models import User
from .services import (
    RoleChangeError,
    is_manager,
    manageable_users,
    set_manager_role,
    set_user_active,
)


class ManagerRequiredMixin(AccessMixin):
    """Require manager access while preserving the manager login entry point."""

    def dispatch(self, request, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect_to_login(
                request.get_full_path(),
                login_url=reverse("manage:login"),
            )
        if not is_manager(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ManagerLoginView(FormView):
    """Authenticate managers through a separate entry point."""

    template_name = "account/manager_login.html"
    form_class = ManagerLoginForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form: ManagerLoginForm) -> HttpResponse:
        login(self.request, form.user)
        redirect_url = self.request.POST.get("next") or self.request.GET.get("next")
        if redirect_url and url_has_allowed_host_and_scheme(
            redirect_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return redirect(redirect_url)
        return redirect("manage:dashboard")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["manager_login"] = True
        return context


class ManagerDashboardView(ManagerRequiredMixin, ListView):
    """List manageable users with manager statistics and filters."""

    model = User
    template_name = "manage/dashboard.html"
    context_object_name = "managed_users"
    paginate_by = 25

    def get_queryset(self):
        queryset = manageable_users().annotate(
            task_count=Count("taskgroups__tasks", distinct=True)
        )
        search = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "")
        role = self.request.GET.get("role", "")

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        if status in {"active", "inactive"}:
            queryset = queryset.filter(is_active=status == "active")
        if role in {User.Role.USER, User.Role.MANAGER}:
            queryset = queryset.filter(role=role)

        return queryset.order_by("username")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        recent_since = now - timedelta(days=7)
        stats = manageable_users().aggregate(
            total_users=Count("pk", filter=Q(role=User.Role.USER)),
            active_users=Count("pk", filter=Q(is_active=True)),
            inactive_users=Count("pk", filter=Q(is_active=False)),
            managers=Count("pk", filter=Q(role=User.Role.MANAGER)),
            recent_signups=Count("pk", filter=Q(date_joined__gte=recent_since)),
        )
        filters = self.request.GET.copy()
        filters.pop("page", None)
        context.update(
            {
                "stats": stats,
                "filter_query": filters.urlencode(),
                "role_choices": User.Role.choices,
                "current_search": self.request.GET.get("q", ""),
                "current_status": self.request.GET.get("status", ""),
                "current_role": self.request.GET.get("role", ""),
            }
        )
        return context


class ManageableUserMixin(ManagerRequiredMixin):
    """Resolve only non-staff, non-superuser accounts."""

    def get_queryset(self):
        return manageable_users()

    def get_object(self, queryset=None):
        user = get_object_or_404(
            queryset or self.get_queryset(),
            pk=self.kwargs["pk"],
        )
        if user.pk == self.request.user.pk:
            raise PermissionDenied
        return user


class ManagerUserDetailView(ManageableUserMixin, DetailView):
    """Show a manageable user's details and read-only tasks."""

    model = User
    template_name = "manage/user_detail.html"
    context_object_name = "managed_user"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tasks = Task.objects.filter(group__user=self.object).select_related("group")
        context["tasks"] = tasks
        context["task_count"] = tasks.count()
        return context


class ManagerUserUpdateView(ManageableUserMixin, UpdateView):
    """Edit a manageable user's basic profile fields."""

    model = User
    form_class = ManagerUserForm
    template_name = "manage/user_form.html"
    context_object_name = "managed_user"
    success_url = reverse_lazy("manage:dashboard")

    def form_valid(self, form: ManagerUserForm) -> HttpResponse:
        messages.success(self.request, "User details updated successfully.")
        return super().form_valid(form)


class ManagerPasswordView(ManageableUserMixin, FormView):
    """Set a manageable user's password without exposing the password."""

    template_name = "manage/password_form.html"
    form_class = ManagerPasswordForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.get_object()
        return kwargs

    def form_valid(self, form: ManagerPasswordForm) -> HttpResponse:
        user = self.get_object()
        user.set_password(form.cleaned_data["new_password1"])
        user.save(update_fields=["password"])
        messages.success(self.request, "Password updated successfully.")
        return redirect("manage:user-detail", pk=user.pk)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["managed_user"] = self.get_object()
        return context


class ManagerRoleView(ManageableUserMixin, View):
    """Promote or demote a manageable user."""

    def post(self, request, pk: int) -> HttpResponse:
        user = self.get_object()
        make_manager = request.POST.get("action") == "make-manager"
        try:
            set_manager_role(request.user, user, make_manager)
        except RoleChangeError as error:
            messages.error(request, str(error))
        else:
            role_name = "manager" if make_manager else "regular user"
            messages.success(request, f"User is now a {role_name}.")
        return redirect("manage:dashboard")


class ManagerActiveView(ManageableUserMixin, View):
    """Activate or deactivate a manageable user."""

    def post(self, request, pk: int) -> HttpResponse:
        user = self.get_object()
        active = request.POST.get("action") == "activate"
        try:
            set_user_active(request.user, user, active)
        except RoleChangeError as error:
            messages.error(request, str(error))
        else:
            messages.success(request, "User status updated successfully.")
        return redirect("manage:dashboard")