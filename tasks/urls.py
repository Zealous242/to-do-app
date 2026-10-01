from django.urls import path

from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='list'),
    path('groups/create/', views.create_task_group, name='group_create'),
    path('groups/<int:group_id>/', views.task_list, name='group'),
    path('categories/', views.category_list, name='category_list'),
    path('category/create/', views.create_category, name='category_create'),
    path('category/<int:pk>/update/', views.update_category, name='category_update'),
    path('category/<int:pk>/delete/', views.delete_category, name='category_delete'),
    path('priority/create/', views.create_priority, name='priority_create'),
    path('priorities/', views.priority_list, name='priority_list'),
    path('priority/<int:pk>/update/', views.update_priority, name='priority_update'),
    path('priority/<int:pk>/delete/', views.delete_priority, name='priority_delete'),
    path('<int:pk>/toggle/', views.toggle_task, name='toggle'),
    path('<int:pk>/edit/', views.edit_task, name='edit'),
    path('<int:pk>/delete/', views.delete_task, name='delete'),
]