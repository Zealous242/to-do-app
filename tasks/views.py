from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CategoryForm, PriorityForm, TaskForm
from .models import Task


def task_list(request):
	if request.method == 'POST':
		form = TaskForm(request.POST)
		if form.is_valid():
			form.save()
		else:
			messages.error(request, 'Enter a task and choose a valid category and priority.')
		return redirect('tasks:list')

	tasks = Task.objects.select_related('category', 'priority').all()
	context = {
		'tasks': tasks,
		'active_tasks': tasks.filter(completed=False),
		'completed_tasks': tasks.filter(completed=True),
		'task_form': TaskForm(),
	}
	return render(request, 'tasks/task_list.html', context)


@require_POST
def toggle_task(request, pk):
	task = get_object_or_404(Task, pk=pk)
	task.completed = not task.completed
	task.save(update_fields=['completed'])
	return redirect('tasks:list')


@require_POST
def delete_task(request, pk):
	task = get_object_or_404(Task, pk=pk)
	task.delete()
	return redirect('tasks:list')


@require_POST
def create_category(request):
	form = CategoryForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, 'Category added.')
	else:
		messages.error(request, 'Enter a unique category name of 60 characters or fewer.')
	return redirect('tasks:list')


@require_POST
def create_priority(request):
	form = PriorityForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, 'Priority added.')
	else:
		messages.error(request, 'Enter a unique priority name of 60 characters or fewer.')
	return redirect('tasks:list')


def edit_task(request, pk):
	task = get_object_or_404(Task, pk=pk)
	form = TaskForm(request.POST or None, instance=task)

	if request.method == 'POST':
		if form.is_valid():
			form.save()
			return redirect('tasks:list')
		messages.error(request, 'Enter a task title and choose a valid category and priority.')

	return render(request, 'tasks/task_edit.html', {'task': task, 'form': form})
