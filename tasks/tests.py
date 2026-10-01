from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Priority, Task, TaskGroup


class TaskListTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='task-user',
			password='A-difficult-password-974!',
		)
		self.client.force_login(self.user)

	def create_task(self, **kwargs):
		return Task.objects.create(user=self.user, **kwargs)

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

	def test_category_and_priority_controls_render_dialog_forms(self):
		response = self.client.get(reverse('tasks:list'))

		self.assertContains(response, 'data-open-dialog="category-dialog"')
		self.assertContains(response, 'id="category-dialog"')
		self.assertContains(response, f'action="{reverse("tasks:category_create")}"')
		self.assertContains(response, 'data-open-dialog="priority-dialog"')
		self.assertContains(response, 'id="priority-dialog"')
		self.assertContains(response, f'action="{reverse("tasks:priority_create")}"')

	def test_user_can_create_a_task_group(self):
		response = self.client.post(reverse('tasks:group_create'), {'name': '  Website refresh  '})

		group = TaskGroup.objects.get(name='Website refresh')
		self.assertEqual(group.user, self.user)
		self.assertRedirects(response, reverse('tasks:group', args=[group.pk]))

	def test_duplicate_task_group_name_is_rejected(self):
		TaskGroup.objects.create(user=self.user, name='Website refresh')

		self.client.post(reverse('tasks:group_create'), {'name': 'website refresh'})

		self.assertEqual(TaskGroup.objects.filter(user=self.user).count(), 1)

	def test_task_group_appears_in_header_navigation(self):
		group = TaskGroup.objects.create(user=self.user, name='Website refresh')

		response = self.client.get(reverse('tasks:list'))

		self.assertContains(response, 'Website refresh')
		self.assertContains(response, reverse('tasks:group', args=[group.pk]))
		self.assertContains(response, 'id="group-create-dialog"')

	def test_group_page_shows_only_its_tasks(self):
		website_group = TaskGroup.objects.create(user=self.user, name='Website refresh')
		move_group = TaskGroup.objects.create(user=self.user, name='Home move')
		website_task = self.create_task(title='Update homepage', group=website_group)
		self.create_task(title='Pack kitchen', group=move_group)

		response = self.client.get(reverse('tasks:group', args=[website_group.pk]))

		self.assertContains(response, website_task.title)
		self.assertNotContains(response, 'Pack kitchen')
		self.assertContains(response, 'PROJECT GROUP')

	def test_task_created_in_group_is_assigned_to_that_group(self):
		group = TaskGroup.objects.create(user=self.user, name='Website refresh')

		response = self.client.post(
			reverse('tasks:group', args=[group.pk]),
			{'title': 'Update homepage', 'group': group.pk},
		)

		task = Task.objects.get(title='Update homepage')
		self.assertEqual(task.group, group)
		self.assertRedirects(response, reverse('tasks:group', args=[group.pk]))

	def test_group_task_actions_return_to_the_group(self):
		group = TaskGroup.objects.create(user=self.user, name='Website refresh')
		task = self.create_task(title='Update homepage', group=group)

		toggle_response = self.client.post(reverse('tasks:toggle', args=[task.pk]))
		self.assertRedirects(toggle_response, reverse('tasks:group', args=[group.pk]))

		delete_response = self.client.post(reverse('tasks:delete', args=[task.pk]))
		self.assertRedirects(delete_response, reverse('tasks:group', args=[group.pk]))

	def test_user_cannot_open_another_users_group(self):
		other_user = get_user_model().objects.create_user(username='other-user')
		group = TaskGroup.objects.create(user=other_user, name='Private project')

		response = self.client.get(reverse('tasks:group', args=[group.pk]))

		self.assertEqual(response.status_code, 404)

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
		active = self.create_task(title='Plan the week')
		completed = self.create_task(title='Water the plants', completed=True)
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
		task = self.create_task(title='Read a chapter')
		url = reverse('tasks:toggle', args=[task.pk])

		self.client.post(url)
		task.refresh_from_db()
		self.assertTrue(task.completed)

		self.client.post(url)
		task.refresh_from_db()
		self.assertFalse(task.completed)

	def test_delete_task_removes_only_selected_task(self):
		task = self.create_task(title='Remove this')
		other_task = self.create_task(title='Keep this')

		response = self.client.post(reverse('tasks:delete', args=[task.pk]))

		self.assertRedirects(response, reverse('tasks:list'))
		self.assertFalse(Task.objects.filter(pk=task.pk).exists())
		self.assertTrue(Task.objects.filter(pk=other_task.pk).exists())

	def test_deleting_missing_task_returns_404(self):
		response = self.client.post(reverse('tasks:delete', args=[999]))

		self.assertEqual(response.status_code, 404)

	def test_edit_task_updates_title(self):
		task = self.create_task(title='Old title')

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
		task = self.create_task(title='Prepare notes', category=old_category)

		self.client.post(
			reverse('tasks:edit', args=[task.pk]),
			{'title': task.title, 'category': new_category.pk},
		)

		task.refresh_from_db()
		self.assertEqual(task.category, new_category)

	def test_edit_task_updates_priority(self):
		old_priority = Priority.objects.create(name='Later')
		new_priority = Priority.objects.create(name='Now')
		task = self.create_task(title='Prepare notes', priority=old_priority)

		self.client.post(
			reverse('tasks:edit', args=[task.pk]),
			{'title': task.title, 'priority': new_priority.pk},
		)

		task.refresh_from_db()
		self.assertEqual(task.priority, new_priority)

	def test_edit_task_updates_description(self):
		task = self.create_task(title='Prepare notes', description='Draft outline')

		self.client.post(
			reverse('tasks:edit', args=[task.pk]),
			{'title': task.title, 'description': 'Add references', 'category': ''},
		)

		task.refresh_from_db()
		self.assertEqual(task.description, 'Add references')

	def test_deleting_category_keeps_task_uncategorized(self):
		category = Category.objects.create(name='Home')
		task = self.create_task(title='Water the plants', category=category)

		category.delete()

		task.refresh_from_db()
		self.assertIsNone(task.category)

	def test_deleting_priority_keeps_task_without_priority(self):
		priority = Priority.objects.create(name='Urgent')
		task = self.create_task(title='Send the proposal', priority=priority)

		priority.delete()

		task.refresh_from_db()
		self.assertIsNone(task.priority)

	def test_new_task_belongs_to_signed_in_user(self):
		self.client.post(reverse('tasks:list'), {'title': 'My task'})

		self.assertEqual(Task.objects.get().user, self.user)

	def test_task_edit_action_renders_modal_with_task_data(self):
		task = self.create_task(title='Review roadmap', description='Check milestones')

		response = self.client.get(reverse('tasks:list'))

		self.assertContains(response, 'id="task-edit-dialog"')
		self.assertContains(response, f'data-edit-url="{reverse("tasks:edit", args=[task.pk])}"')
		self.assertContains(response, 'data-title="Review roadmap"')
		self.assertContains(response, 'data-description="Check milestones"')
		self.assertContains(response, 'tasks/task_list.js')

	def test_task_list_hides_another_users_tasks(self):
		other_user = get_user_model().objects.create_user(username='other-user')
		Task.objects.create(user=other_user, title='Private task')

		response = self.client.get(reverse('tasks:list'))

		self.assertNotContains(response, 'Private task')

	def test_cannot_edit_another_users_task(self):
		other_user = get_user_model().objects.create_user(username='other-user')
		task = Task.objects.create(user=other_user, title='Private task')

		response = self.client.post(reverse('tasks:edit', args=[task.pk]), {'title': 'Changed'})

		self.assertEqual(response.status_code, 404)
		task.refresh_from_db()
		self.assertEqual(task.title, 'Private task')

	def test_cannot_toggle_or_delete_another_users_task(self):
		other_user = get_user_model().objects.create_user(username='other-user')
		task = Task.objects.create(user=other_user, title='Private task')

		toggle_response = self.client.post(reverse('tasks:toggle', args=[task.pk]))
		delete_response = self.client.post(reverse('tasks:delete', args=[task.pk]))

		self.assertEqual(toggle_response.status_code, 404)
		self.assertEqual(delete_response.status_code, 404)
		self.assertTrue(Task.objects.filter(pk=task.pk).exists())


class AccountTests(TestCase):
	def test_existing_user_can_sign_in(self):
		get_user_model().objects.create_user(
			username='returning-user',
			password='A-difficult-password-974!',
		)

		response = self.client.post(
			reverse('login'),
			{'username': 'returning-user', 'password': 'A-difficult-password-974!'},
		)

		self.assertRedirects(response, reverse('tasks:list'))
		self.assertTrue(response.wsgi_request.user.is_authenticated)

	def test_signed_in_user_can_sign_out(self):
		user = get_user_model().objects.create_user(
			username='returning-user',
			password='A-difficult-password-974!',
		)
		self.client.force_login(user)

		response = self.client.post(reverse('logout'))

		self.assertRedirects(response, reverse('login'))
		self.assertFalse(response.wsgi_request.user.is_authenticated)

	def test_signup_creates_user_and_signs_them_in(self):
		response = self.client.post(
			reverse('signup'),
			{
				'username': 'new-user',
				'password1': 'A-difficult-password-974!',
				'password2': 'A-difficult-password-974!',
			},
		)

		self.assertRedirects(response, reverse('tasks:list'))
		self.assertTrue(response.wsgi_request.user.is_authenticated)
		self.assertTrue(get_user_model().objects.filter(username='new-user').exists())

	def test_signin_page_is_available(self):
		response = self.client.get(reverse('login'))

		self.assertContains(response, 'Sign in.')
		self.assertContains(response, 'Create an account')

	def test_task_list_redirects_anonymous_users_to_signin(self):
		response = self.client.get(reverse('tasks:list'))

		self.assertRedirects(response, f"{reverse('login')}?next={reverse('tasks:list')}")
