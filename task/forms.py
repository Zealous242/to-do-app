"""Forms for creating and updating individual tasks."""

from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    """Form to create and update tasks."""

    class Meta:
        model = Task
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter task title...",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Add some details...",
                    "rows": 3,
                }
            ),
        }