from django import forms

from .models import Category, Priority, Task


class TaskForm(forms.ModelForm):
	class Meta:
		model = Task
		fields = ['title', 'category', 'priority', 'description']
		widgets = {
			'title': forms.TextInput(attrs={
				'maxlength': 200,
				'placeholder': 'What needs your attention?',
			}),
			'category': forms.Select(),
			'priority': forms.Select(),
			'description': forms.Textarea(attrs={
				'rows': 3,
				'placeholder': 'Add steps, notes, or useful details.',
			}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['category'].queryset = Category.objects.order_by('name')
		self.fields['category'].required = False
		self.fields['category'].empty_label = 'No category'
		self.fields['priority'].queryset = Priority.objects.order_by('name')
		self.fields['priority'].required = False
		self.fields['priority'].empty_label = 'No priority'


class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = ['name']
		widgets = {
			'name': forms.TextInput(attrs={
				'maxlength': 60,
				'placeholder': 'Category name',
			}),
		}


class PriorityForm(forms.ModelForm):
	class Meta:
		model = Priority
		fields = ['name']
		widgets = {
			'name': forms.TextInput(attrs={
				'maxlength': 60,
				'placeholder': 'Priority name',
			}),
		}