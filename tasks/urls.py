from django.urls import path

from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='list'),
    path('category/create/', views.create_category, name='category_create'),
    path('priority/create/', views.create_priority, name='priority_create'),
    path('<int:pk>/toggle/', views.toggle_task, name='toggle'),
    path('<int:pk>/edit/', views.edit_task, name='edit'),
    path('<int:pk>/delete/', views.delete_task, name='delete'),
]