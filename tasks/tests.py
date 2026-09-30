from django.test import TestCase
from django.urls import reverse

from .models import Category, Priority, Task


class TaskListTests(TestCase):
	def test_empty_list_shows_empty_state(self):
		response = self.client.get(reverse('tasks:list'))

		self.assertContains(response, 'No tasks yet!')

	def test_create_task_strips_whitespace_and_redirects(self):
		response = self.client.post(reverse('tasks:list'), {'title': '  Buy milk  '})

		self.assertRedirects(response, reverse('tasks:list'))
		self.assertEqual(Task.objects.get().title, 'Buy milk')

	def test_create_task_with_category(self):
		category = Category.objects.create(name='Home')

		self.client.post(
			reverse('tasks:list'),
			{'title': 'Water the plants', 'category': category.pk},
		)

		task = Task.objects.get()
		self.assertEqual(task.category, category)

	def test_create_task_with_priority(self):
		priority = Priority.objects.create(name='Urgent')

		self.client.post(
			reverse('tasks:list'),
			{'title': 'Send the proposal', 'priority': priority.pk},
		)

		self.assertEqual(Task.objects.get().priority, priority)

	def test_create_task_with_description(self):
		self.client.post(
			reverse('tasks:list'),
			{'title': 'Clean the desk', 'description': 'Sort papers and wipe the surface.'},
		)

		self.assertEqual(Task.objects.get().description, 'Sort papers and wipe the surface.')

	def test_category_can_be_created_from_the_list(self):
		response = self.client.post(
			reverse('tasks:category_create'),
			{'name': '  Study  '},
		)

		self.assertRedirects(response, reverse('tasks:list'))
		self.assertTrue(Category.objects.filter(name='Study').exists())

	def test_duplicate_category_is_not_created(self):
		Category.objects.create(name='Work')

		self.client.post(reverse('tasks:category_create'), {'name': 'Work'})

		self.assertEqual(Category.objects.count(), 1)

	def test_priority_can_be_created_from_the_list(self):
		response = self.client.post(
			reverse('tasks:priority_create'),
			{'name': '  Urgent  '},
		)

		self.assertRedirects(response, reverse('tasks:list'))
		self.assertTrue(Priority.objects.filter(name='Urgent').exists())

	def test_duplicate_priority_is_not_created(self):
		Priority.objects.create(name='Next')

		self.client.post(reverse('tasks:priority_create'), {'name': 'Next'})

		self.assertEqual(Priority.objects.count(), 1)

	def test_whitespace_only_task_is_rejected(self):
		self.client.post(reverse('tasks:list'), {'title': '   '})

		self.assertFalse(Task.objects.exists())

	def test_task_list_shows_active_and_completed_tasks(self):
		active = Task.objects.create(title='Plan the week')
		completed = Task.objects.create(title='Water the plants', completed=True)
		active.priority = Priority.objects.create(name='Important')
		active.description = 'Review the calendar first.'
		active.save(update_fields=['description', 'priority'])

		response = self.client.get(reverse('tasks:list'))

		self.assertContains(response, active.title)
		self.assertContains(response, active.description)
		self.assertContains(response, active.priority.name)
		self.assertContains(response, completed.title)
		self.assertContains(response, 'Undo')

	def test_toggle_task_completes_and_reopens_task(self):
		task = Task.objects.create(title='Read a chapter')
		url = reverse('tasks:toggle', args=[task.pk])

		self.client.post(url)
		task.refresh_from_db()
		self.assertTrue(task.completed)

		self.client.post(url)
		task.refresh_from_db()
		self.assertFalse(task.completed)

	def test_delete_task_removes_only_selected_task(self):
		task = Task.objects.create(title='Remove this')
		other_task = Task.objects.create(title='Keep this')

		response = self.client.post(reverse('tasks:delete', args=[task.pk]))

		self.assertRedirects(response, reverse('tasks:list'))
		self.assertFalse(Task.objects.filter(pk=task.pk).exists())
		self.assertTrue(Task.objects.filter(pk=other_task.pk).exists())

	def test_deleting_missing_task_returns_404(self):
		response = self.client.post(reverse('tasks:delete', args=[999]))

		self.assertEqual(response.status_code, 404)

	def test_edit_task_updates_title(self):
		task = Task.objects.create(title='Old title')

		response = self.client.post(
			reverse('tasks:edit', args=[task.pk]),
			{'title': 'New title'},
		)

		self.assertRedirects(response, reverse('tasks:list'))
		task.refresh_from_db()
		self.assertEqual(task.title, 'New title')

	def test_edit_task_updates_category(self):
		old_category = Category.objects.create(name='Home')
		new_category = Category.objects.create(name='Work')
		task = Task.objects.create(title='Prepare notes', category=old_category)

		self.client.post(
			reverse('tasks:edit', args=[task.pk]),
			{'title': task.title, 'category': new_category.pk},
		)

		task.refresh_from_db()
		self.assertEqual(task.category, new_category)

	def test_edit_task_updates_priority(self):
		old_priority = Priority.objects.create(name='Later')
		new_priority = Priority.objects.create(name='Now')
		task = Task.objects.create(title='Prepare notes', priority=old_priority)

		self.client.post(
			reverse('tasks:edit', args=[task.pk]),
			{'title': task.title, 'priority': new_priority.pk},
		)

		task.refresh_from_db()
		self.assertEqual(task.priority, new_priority)

	def test_edit_task_updates_description(self):
		task = Task.objects.create(title='Prepare notes', description='Draft outline')

		self.client.post(
			reverse('tasks:edit', args=[task.pk]),
			{'title': task.title, 'description': 'Add references', 'category': ''},
		)

		task.refresh_from_db()
		self.assertEqual(task.description, 'Add references')

	def test_deleting_category_keeps_task_uncategorized(self):
		category = Category.objects.create(name='Home')
		task = Task.objects.create(title='Water the plants', category=category)

		category.delete()

		task.refresh_from_db()
		self.assertIsNone(task.category)

	def test_deleting_priority_keeps_task_without_priority(self):
		priority = Priority.objects.create(name='Urgent')
		task = Task.objects.create(title='Send the proposal', priority=priority)

		priority.delete()

		task.refresh_from_db()
		self.assertIsNone(task.priority)
