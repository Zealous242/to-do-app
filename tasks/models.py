from django.conf import settings
from django.db import models


class Category(models.Model):
	name = models.CharField(max_length=60, unique=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class Priority(models.Model):
	name = models.CharField(max_length=60, unique=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class TaskGroup(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='task_groups',
	)
	name = models.CharField(max_length=80)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['name', 'pk']
		constraints = [
			models.UniqueConstraint(fields=['user', 'name'], name='unique_task_group_name_per_user'),
		]

	def __str__(self):
		return self.name


class Task(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='tasks',
		blank=True,
		null=True,
	)
	group = models.ForeignKey(
		TaskGroup,
		on_delete=models.SET_NULL,
		related_name='tasks',
		blank=True,
		null=True,
	)
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True, default='')
	category = models.ForeignKey(
		Category,
		on_delete=models.SET_NULL,
		related_name='tasks',
		blank=True,
		null=True,
	)
	priority = models.ForeignKey(
		Priority,
		on_delete=models.SET_NULL,
		related_name='tasks',
		blank=True,
		null=True,
	)
	completed = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['completed', '-created_at', '-pk']

	def __str__(self):
		return self.title
