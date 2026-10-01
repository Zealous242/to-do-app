from django import forms

from .models import Category, Priority, Task, TaskGroup


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


class TaskGroupForm(forms.ModelForm):
	class Meta:
		model = TaskGroup
		fields = ['name']
		widgets = {
			'name': forms.TextInput(attrs={
				'maxlength': 80,
				'placeholder': 'e.g. Website refresh, Home move',
			}),
		}

	def __init__(self, *args, user, **kwargs):
		super().__init__(*args, **kwargs)
		self.user = user

	def clean_name(self):
		name = self.cleaned_data['name']
		if TaskGroup.objects.filter(user=self.user, name__iexact=name).exists():
			raise forms.ValidationError('You already have a group with this name.')
		return name