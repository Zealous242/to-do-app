from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import F
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import CategoryForm, PriorityForm, TaskForm, TaskGroupForm
from .models import Category, Priority, Task, TaskGroup


def _task_list_redirect(group_id=None):
	if group_id:
		return redirect('tasks:group', group_id)
	return redirect('tasks:list')


def _filter_remove_url(request, list_url, filter_name):
	query = request.GET.copy()
	query.pop(filter_name, None)
	for key in ('priority', 'category'):
		if not query.get(key):
			query.pop(key, None)
	if query.get('sort') == 'recent':
		query.pop('sort', None)
	query_string = query.urlencode()
	return f'{list_url}?{query_string}' if query_string else list_url


@login_required
def task_list(request, group_id=None):
	selected_group = None
	if group_id is not None:
		selected_group = get_object_or_404(TaskGroup, pk=group_id, user=request.user)

	if request.method == 'POST':
		posted_group_id = request.POST.get('group')
		if posted_group_id:
			selected_group = get_object_or_404(TaskGroup, pk=posted_group_id, user=request.user)
		form = TaskForm(request.POST)
		if form.is_valid():
			task = form.save(commit=False)
			task.user = request.user
			task.group = selected_group
			task.save()
		else:
			messages.error(request, 'Enter a task and choose a valid category and priority.')
		return _task_list_redirect(selected_group.pk if selected_group else None)

	tasks = Task.objects.filter(user=request.user)
	if selected_group:
		tasks = tasks.filter(group=selected_group)

	priority_options = Priority.objects.order_by('name')
	priority_filter = request.GET.get('priority', '')
	selected_priority = None
	if priority_filter == 'unassigned':
		tasks = tasks.filter(priority__isnull=True)
	elif priority_filter:
		selected_priority = priority_options.filter(pk=priority_filter).first()
		if selected_priority:
			tasks = tasks.filter(priority=selected_priority)
		else:
			priority_filter = ''

	category_options = Category.objects.order_by('name')
	category_filter = request.GET.get('category', '')
	selected_category = None
	if category_filter == 'unassigned':
		tasks = tasks.filter(category__isnull=True)
	elif category_filter:
		selected_category = category_options.filter(pk=category_filter).first()
		if selected_category:
			tasks = tasks.filter(category=selected_category)
		else:
			category_filter = ''

	sort_order = request.GET.get('sort', 'recent')
	if sort_order == 'title_asc':
		tasks = tasks.order_by(Lower('title').asc(), '-created_at', '-pk')
	elif sort_order == 'title_desc':
		tasks = tasks.order_by(Lower('title').desc(), '-created_at', '-pk')
	elif sort_order == 'created_asc':
		tasks = tasks.order_by('created_at', 'pk')
	elif sort_order == 'created_desc':
		tasks = tasks.order_by('-created_at', '-pk')
	elif sort_order == 'priority_asc':
		tasks = tasks.order_by(F('priority__name').asc(nulls_last=True), '-created_at', '-pk')
	elif sort_order == 'priority_desc':
		tasks = tasks.order_by(F('priority__name').desc(nulls_last=True), '-created_at', '-pk')
	else:
		sort_order = 'recent'

	tasks = tasks.select_related('category', 'priority', 'group')
	list_url = reverse('tasks:group', args=[selected_group.pk]) if selected_group else reverse('tasks:list')
	active_filters = []
	if priority_filter:
		priority_label = selected_priority.name if selected_priority else 'No priority'
		active_filters.append({
			'label': f'Priority: {priority_label}',
			'remove_url': _filter_remove_url(request, list_url, 'priority'),
			'aria_label': 'Remove priority filter',
		})
	if category_filter:
		category_label = selected_category.name if selected_category else 'No category'
		active_filters.append({
			'label': f'Category: {category_label}',
			'remove_url': _filter_remove_url(request, list_url, 'category'),
			'aria_label': 'Remove category filter',
		})
	context = {
		'tasks': tasks,
		'active_tasks': tasks.filter(completed=False),
		'completed_tasks': tasks.filter(completed=True),
		'task_form': TaskForm(),
		'edit_form': TaskForm(auto_id='edit_%s'),
		'task_groups': request.user.task_groups.all(),
		'selected_group': selected_group,
		'priority_options': priority_options,
		'priority_filter': priority_filter,
		'selected_priority': selected_priority,
		'category_options': category_options,
		'category_filter': category_filter,
		'selected_category': selected_category,
		'active_filters': active_filters,
		'sort_order': sort_order,
		'list_url': list_url,
	}
	return render(request, 'tasks/task_list.html', context)


@login_required
@require_POST
def toggle_task(request, pk):
	task = get_object_or_404(Task, pk=pk, user=request.user)
	task.completed = not task.completed
	task.save(update_fields=['completed'])
	return _task_list_redirect(task.group_id)


@login_required
@require_POST
def delete_task(request, pk):
	task = get_object_or_404(Task, pk=pk, user=request.user)
	group_id = task.group_id
	task.delete()
	return _task_list_redirect(group_id)


@login_required
@require_POST
def create_category(request):
	group_id = request.POST.get('group') or None
	if group_id:
		get_object_or_404(TaskGroup, pk=group_id, user=request.user)
	form = CategoryForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, 'Category added.')
	else:
		messages.error(request, 'Enter a unique category name of 60 characters or fewer.')
	return _task_list_redirect(group_id)


@login_required
@require_POST
def create_priority(request):
	group_id = request.POST.get('group') or None
	if group_id:
		get_object_or_404(TaskGroup, pk=group_id, user=request.user)
	form = PriorityForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, 'Priority added.')
	else:
		messages.error(request, 'Enter a unique priority name of 60 characters or fewer.')
	return _task_list_redirect(group_id)


@login_required
@require_POST
def create_task_group(request):
	form = TaskGroupForm(request.POST, user=request.user)
	if form.is_valid():
		group = form.save(commit=False)
		group.user = request.user
		group.save()
		messages.success(request, f'{group.name} group created.')
		return _task_list_redirect(group.pk)

	messages.error(request, 'Enter a unique group name of 80 characters or fewer.')
	return redirect('tasks:list')


@login_required
def edit_task(request, pk):
	task = get_object_or_404(Task, pk=pk, user=request.user)
	form = TaskForm(request.POST or None, instance=task)

	if request.method == 'POST':
		if form.is_valid():
			form.save()
			return _task_list_redirect(task.group_id)
		messages.error(request, 'Enter a task title and choose a valid category and priority.')
		if request.POST.get('modal') == '1':
			return _task_list_redirect(task.group_id)

	return render(request, 'tasks/task_edit.html', {
		'task': task,
		'form': form,
		'task_groups': request.user.task_groups.all(),
		'selected_group': task.group,
	})


def signup(request):
	if request.user.is_authenticated:
		return redirect('tasks:list')

	form = UserCreationForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		user = form.save()
		login(request, user)
		return redirect('tasks:list')

	return render(request, 'registration/signup.html', {'form': form})
