from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CategoryForm, PriorityForm, TaskForm, TaskGroupForm
from .models import Task, TaskGroup


def _task_list_redirect(group_id=None):
	if group_id:
		return redirect('tasks:group', group_id)
	return redirect('tasks:list')


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
	tasks = tasks.select_related('category', 'priority', 'group')
	context = {
		'tasks': tasks,
		'active_tasks': tasks.filter(completed=False),
		'completed_tasks': tasks.filter(completed=True),
		'task_form': TaskForm(),
		'edit_form': TaskForm(auto_id='edit_%s'),
		'task_groups': request.user.task_groups.all(),
		'selected_group': selected_group,
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
