from django.urls import path
from .views import register, login_view, logout_view, create_task, update_task, mark_task_completed, soft_delete_task, list_tasks

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('tasks/', create_task, name='create_task'),
    path('tasks/<int:task_id>/', update_task, name='update_task'), 
    path('tasks/<int:task_id>/complete/', mark_task_completed, name='mark_task_completed'),
    path('tasks/<int:task_id>/delete/', soft_delete_task, name='soft_delete_task'),
    path('tasks/list/', list_tasks, name='list_tasks'),
]
