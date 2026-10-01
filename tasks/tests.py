from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format

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

	def test_creating_task_displays_bootstrap_success_alert(self):
		response = self.client.post(reverse('tasks:list'), {'title': 'Buy milk'})

		list_response = self.client.get(response.url)

		self.assertContains(list_response, 'alert-success')
		self.assertContains(list_response, 'Task added successfully.')

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

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse('tasks:list'))
		self.assertTrue(Category.objects.filter(name='Study').exists())
		list_response = self.client.get(response.url)
		self.assertContains(list_response, 'alert-success')
		self.assertContains(list_response, 'Category added.')

	def test_category_management_page_lists_categories_and_task_counts(self):
		category = Category.objects.create(name='Study')
		self.create_task(title='Review notes', category=category)

		response = self.client.get(reverse('tasks:category_list'))

		self.assertContains(response, 'Manage categories.')
		self.assertContains(response, 'Study')
		self.assertContains(response, '1 task')

	def test_category_can_be_updated_without_unlinking_tasks(self):
		category = Category.objects.create(name='Study')
		task = self.create_task(title='Review notes', category=category)

		response = self.client.post(
			reverse('tasks:category_update', args=[category.pk]),
			{'name': 'Learning'},
		)
		list_response = self.client.get(response.url)

		category.refresh_from_db()
		task.refresh_from_db()
		self.assertEqual(category.name, 'Learning')
		self.assertEqual(task.category, category)
		self.assertContains(list_response, 'alert-success')
		self.assertContains(list_response, 'Category updated.')

	def test_category_can_be_deleted_and_tasks_become_uncategorized(self):
		category = Category.objects.create(name='Study')
		task = self.create_task(title='Review notes', category=category)

		response = self.client.post(reverse('tasks:category_delete', args=[category.pk]))
		list_response = self.client.get(response.url)

		self.assertFalse(Category.objects.filter(pk=category.pk).exists())
		task.refresh_from_db()
		self.assertIsNone(task.category)
		self.assertContains(list_response, 'Category deleted.')

	def test_manage_categories_link_is_available_from_task_list(self):
		response = self.client.get(reverse('tasks:list'))

		self.assertContains(response, reverse('tasks:category_list'))

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
		self.assertContains(response, '<details class="group-menu">')
		self.assertContains(response, 'summary class="group-menu-trigger"')
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

	def test_tasks_can_be_filtered_by_priority(self):
		high_priority = Priority.objects.create(name='High')
		self.create_task(title='Urgent paperwork', priority=high_priority)
		self.create_task(title='Later reading', priority=Priority.objects.create(name='Low'))

		response = self.client.get(reverse('tasks:list'), {'priority': high_priority.pk})

		self.assertEqual(list(response.context['tasks'].values_list('title', flat=True)), ['Urgent paperwork'])
		self.assertEqual(response.context['selected_priority'], high_priority)

	def test_tasks_without_priority_can_be_filtered(self):
		self.create_task(title='Unassigned task')
		self.create_task(title='Prioritized task', priority=Priority.objects.create(name='High'))

		response = self.client.get(reverse('tasks:list'), {'priority': 'unassigned'})

		self.assertEqual(list(response.context['tasks'].values_list('title', flat=True)), ['Unassigned task'])
		self.assertContains(response, 'Unassigned task')
		self.assertNotContains(response, 'Prioritized task')

	def test_tasks_can_be_filtered_by_category(self):
		home_category = Category.objects.create(name='Home')
		self.create_task(title='Water plants', category=home_category)
		self.create_task(title='Send invoice', category=Category.objects.create(name='Work'))

		response = self.client.get(reverse('tasks:list'), {'category': home_category.pk})

		self.assertEqual(list(response.context['tasks'].values_list('title', flat=True)), ['Water plants'])
		self.assertEqual(response.context['selected_category'], home_category)
		self.assertContains(response, 'All categories')

	def test_tasks_without_category_can_be_filtered(self):
		self.create_task(title='Uncategorized task')
		self.create_task(title='Home task', category=Category.objects.create(name='Home'))

		response = self.client.get(reverse('tasks:list'), {'category': 'unassigned'})

		self.assertEqual(list(response.context['tasks'].values_list('title', flat=True)), ['Uncategorized task'])
		self.assertContains(response, 'No category')

	def test_category_filter_combines_with_priority_and_group(self):
		group = TaskGroup.objects.create(user=self.user, name='Website refresh')
		category = Category.objects.create(name='Design')
		priority = Priority.objects.create(name='High')
		self.create_task(title='Project design task', group=group, category=category, priority=priority)
		self.create_task(title='Other category task', group=group, priority=priority)
		self.create_task(title='Outside group task', category=category, priority=priority)

		response = self.client.get(
			reverse('tasks:group', args=[group.pk]),
			{'category': category.pk, 'priority': priority.pk, 'sort': 'title_asc'},
		)

		self.assertEqual(list(response.context['tasks'].values_list('title', flat=True)), ['Project design task'])
		self.assertEqual(response.context['selected_category'], category)
		self.assertEqual(response.context['selected_priority'], priority)

	def test_active_filter_chips_remove_one_filter_and_preserve_the_rest(self):
		category = Category.objects.create(name='Design')
		priority = Priority.objects.create(name='High')
		response = self.client.get(
			reverse('tasks:list'),
			{'category': category.pk, 'priority': priority.pk, 'sort': 'title_asc'},
		)

		self.assertContains(response, 'Category: Design')
		self.assertContains(response, 'Priority: High')
		chips_by_label = {chip['label']: chip for chip in response.context['active_filters']}
		category_chip = chips_by_label['Category: Design']
		priority_chip = chips_by_label['Priority: High']
		self.assertIn(f'priority={priority.pk}', category_chip['remove_url'])
		self.assertIn('sort=title_asc', category_chip['remove_url'])
		self.assertNotIn('category=', category_chip['remove_url'])
		self.assertIn(f'category={category.pk}', priority_chip['remove_url'])
		self.assertIn('sort=title_asc', priority_chip['remove_url'])
		self.assertNotIn('priority=', priority_chip['remove_url'])

	def test_tasks_can_be_sorted_by_priority_name(self):
		self.create_task(title='Zulu task', priority=Priority.objects.create(name='Zulu'))
		self.create_task(title='Alpha task', priority=Priority.objects.create(name='Alpha'))
		self.create_task(title='No priority task')

		ascending_response = self.client.get(reverse('tasks:list'), {'sort': 'priority_asc'})
		descending_response = self.client.get(reverse('tasks:list'), {'sort': 'priority_desc'})

		ascending_titles = list(ascending_response.context['active_tasks'].values_list('title', flat=True))
		descending_titles = list(descending_response.context['active_tasks'].values_list('title', flat=True))
		self.assertEqual(ascending_titles, ['Alpha task', 'Zulu task', 'No priority task'])
		self.assertEqual(descending_titles, ['Zulu task', 'Alpha task', 'No priority task'])

	def test_tasks_can_be_sorted_by_date_created(self):
		oldest = self.create_task(title='Oldest task')
		middle = self.create_task(title='Middle task')
		newest = self.create_task(title='Newest task')
		current_time = timezone.now()
		Task.objects.filter(pk=oldest.pk).update(created_at=current_time - timedelta(days=3))
		Task.objects.filter(pk=middle.pk).update(created_at=current_time - timedelta(days=2))
		Task.objects.filter(pk=newest.pk).update(created_at=current_time - timedelta(days=1))

		oldest_first = self.client.get(reverse('tasks:list'), {'sort': 'created_asc'})
		newest_first = self.client.get(reverse('tasks:list'), {'sort': 'created_desc'})

		self.assertEqual(
			list(oldest_first.context['active_tasks'].values_list('title', flat=True)),
			['Oldest task', 'Middle task', 'Newest task'],
		)
		self.assertEqual(
			list(newest_first.context['active_tasks'].values_list('title', flat=True)),
			['Newest task', 'Middle task', 'Oldest task'],
		)
		self.assertContains(oldest_first, 'Date created, oldest first')
		self.assertContains(newest_first, 'Date created, newest first')

	def test_tasks_can_be_sorted_alphabetically_case_insensitive(self):
		self.create_task(title='Banana task')
		self.create_task(title='apple task')
		self.create_task(title='Cherry task')

		ascending = self.client.get(reverse('tasks:list'), {'sort': 'title_asc'})
		descending = self.client.get(reverse('tasks:list'), {'sort': 'title_desc'})

		self.assertEqual(
			list(ascending.context['active_tasks'].values_list('title', flat=True)),
			['apple task', 'Banana task', 'Cherry task'],
		)
		self.assertEqual(
			list(descending.context['active_tasks'].values_list('title', flat=True)),
			['Cherry task', 'Banana task', 'apple task'],
		)
		self.assertContains(ascending, 'Task name, A to Z')
		self.assertContains(descending, 'Task name, Z to A')

	def test_priority_filter_is_limited_to_selected_group(self):
		group = TaskGroup.objects.create(user=self.user, name='Website refresh')
		priority = Priority.objects.create(name='High')
		self.create_task(title='In project', group=group, priority=priority)
		self.create_task(title='Outside project', priority=priority)

		response = self.client.get(reverse('tasks:group', args=[group.pk]), {'priority': priority.pk})

		self.assertContains(response, 'In project')
		self.assertNotContains(response, 'Outside project')
		self.assertEqual(response.context['list_url'], reverse('tasks:group', args=[group.pk]))

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

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse('tasks:list'))
		self.assertTrue(Priority.objects.filter(name='Urgent').exists())
		list_response = self.client.get(response.url)
		self.assertContains(list_response, 'alert-success')
		self.assertContains(list_response, 'Priority added.')

	def test_duplicate_priority_is_not_created(self):
		Priority.objects.create(name='Next')

		self.client.post(reverse('tasks:priority_create'), {'name': 'Next'})

		self.assertEqual(Priority.objects.count(), 1)

	def test_priority_management_page_lists_priorities_and_task_counts(self):
		priority = Priority.objects.create(name='High')
		self.create_task(title='Important task', priority=priority)

		response = self.client.get(reverse('tasks:priority_list'))

		self.assertContains(response, 'Manage priorities.')
		self.assertContains(response, 'High')
		self.assertContains(response, '1 task')

	def test_priority_can_be_updated_without_unlinking_tasks(self):
		priority = Priority.objects.create(name='High')
		task = self.create_task(title='Important task', priority=priority)

		response = self.client.post(
			reverse('tasks:priority_update', args=[priority.pk]),
			{'name': 'Urgent'},
		)
		list_response = self.client.get(response.url)

		priority.refresh_from_db()
		task.refresh_from_db()
		self.assertEqual(priority.name, 'Urgent')
		self.assertEqual(task.priority, priority)
		self.assertContains(list_response, 'alert-success')
		self.assertContains(list_response, 'Priority updated.')

	def test_priority_can_be_deleted_and_tasks_become_unprioritized(self):
		priority = Priority.objects.create(name='High')
		task = self.create_task(title='Important task', priority=priority)

		response = self.client.post(reverse('tasks:priority_delete', args=[priority.pk]))
		list_response = self.client.get(response.url)

		self.assertFalse(Priority.objects.filter(pk=priority.pk).exists())
		task.refresh_from_db()
		self.assertIsNone(task.priority)
		self.assertContains(list_response, 'Priority deleted.')

	def test_manage_priorities_link_is_available_from_task_list(self):
		response = self.client.get(reverse('tasks:list'))

		self.assertContains(response, reverse('tasks:priority_list'))

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
		self.assertContains(response, f'Created {date_format(active.created_at, "M j, Y")}')
		self.assertContains(response, completed.title)
		self.assertContains(response, f'Created {date_format(completed.created_at, "M j, Y")}')
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

	def test_delete_task_displays_red_bootstrap_alert(self):
		task = self.create_task(title='Remove this')

		response = self.client.post(reverse('tasks:delete', args=[task.pk]))
		list_response = self.client.get(response.url)

		self.assertContains(list_response, 'alert-danger')
		self.assertContains(list_response, 'Task deleted.')

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

	def test_edit_task_displays_blue_bootstrap_alert(self):
		task = self.create_task(title='Old title')

		response = self.client.post(
			reverse('tasks:edit', args=[task.pk]),
			{'title': 'Updated title'},
		)
		list_response = self.client.get(response.url)

		self.assertContains(list_response, 'alert-info')
		self.assertContains(list_response, 'Task updated.')

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
