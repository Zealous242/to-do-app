"""Forms for creating, updating, filtering, and managing individual tasks."""

from typing import Any

from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    """Form to create and update Task instances."""

    class Meta:
        model = Task
        fields = ["title", "parent", "status", "description"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter task title...",
                }
            ),
            "parent": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Task details, acceptance criteria, or notes...",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args: Any, taskgroup=None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Limit parent choices to tasks in the current project.
        self.fields["parent"].empty_label = "None (Top-level Task)"
        if taskgroup is not None:
            self.fields["parent"].queryset = Task.objects.filter(group=taskgroup)

        # Exclude current task from being selected as its own parent when editing
        if self.instance and self.instance.pk:
            self.fields["parent"].queryset = Task.objects.exclude(pk=self.instance.pk)

    def clean_parent(self) -> Task | None:
        """Ensure a task cannot be set as its own parent or cause immediate circular links."""
        parent = self.cleaned_data.get("parent")

        if parent and self.instance and self.instance.pk:
            if parent.pk == self.instance.pk:
                raise forms.ValidationError("A task cannot be set as its own parent.")

            # Simple check to prevent immediate 2-level cyclic dependency
            if parent.parent_id == self.instance.pk:
                raise forms.ValidationError(
                    "Circular reference detected: selected parent is already a subtask of this task."
                )

        return parent
