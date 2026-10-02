"""Forms for user registration, profiles, and manager authentication workflows."""

from typing import Any

from allauth.account.forms import LoginForm
from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import User
from .services import is_manager


class ManagerLoginForm(LoginForm):
	"""Authenticate through the manager entry point only."""

	def clean(self) -> dict[str, Any]:
		cleaned_data = super().clean()
		if self.user and not is_manager(self.user):
			raise forms.ValidationError("You do not have manager access")
		return cleaned_data


class ManagerUserForm(forms.ModelForm):
	"""Edit the profile fields a manager may change."""

	class Meta:
		model = User
		fields = ["username", "email", "first_name", "last_name"]
		widgets = {
			field: forms.TextInput(attrs={"class": "form-control"})
			for field in ["username", "email", "first_name", "last_name"]
		}


class ManagerPasswordForm(forms.Form):
	"""Set a new password after validating it with Django's validators."""

	new_password1 = forms.CharField(
		label="New password",
		widget=forms.PasswordInput(attrs={"class": "form-control"}),
	)
	new_password2 = forms.CharField(
		label="Confirm new password",
		widget=forms.PasswordInput(attrs={"class": "form-control"}),
	)

	def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
		self.user = user
		super().__init__(*args, **kwargs)

	def clean(self) -> dict[str, Any]:
		cleaned_data = super().clean()
		password = cleaned_data.get("new_password1")
		confirmation = cleaned_data.get("new_password2")

		if password and confirmation and password != confirmation:
			self.add_error("new_password2", "The passwords do not match.")
		if password:
			validate_password(password, self.user)

		return cleaned_data
