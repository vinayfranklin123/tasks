from django.urls import path
from .views import create_task, update_task, mark_task_completed, soft_delete_task, list_tasks

urlpatterns = [
    path('create/', create_task, name='create_task'),
    path('update/<int:task_id>/', update_task, name='update_task'),
    path('complete/<int:task_id>/', mark_task_completed, name='mark_task_completed'),
    path('delete/<int:task_id>/', soft_delete_task, name='soft_delete_task'),
    path('list/', list_tasks, name='list_tasks'),
]
