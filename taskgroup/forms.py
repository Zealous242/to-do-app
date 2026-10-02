"""Forms for creating projects, assigning task groups, and setting group visibility."""

from django import forms

from .models import TaskGroup


class TaskGroupForm(forms.ModelForm):
	"""Form for creating a project."""

	class Meta:
		model = TaskGroup
		fields = ["name", "description"]
		widgets = {
			"name": forms.TextInput(
				attrs={"placeholder": "Project name", "required": True}
			),
			"description": forms.Textarea(
				attrs={"placeholder": "What is this project about?", "rows": 3}
			),
		}
