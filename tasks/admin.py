from django.contrib import admin

from .models import Category, Priority, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	search_fields = ['name']


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
	search_fields = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = ['title', 'category', 'priority', 'completed', 'created_at']
	list_filter = ['category', 'priority', 'completed']
	search_fields = ['title']
