from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from tasks.models import Task  
from django.utils import timezone
from datetime import timedelta
import json

class TaskTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.task = Task.objects.create(
            user=self.user,
            name='Test Task',
            description='Task description',
            to_be_completed_time='2024-08-01T10:00:00Z'
        )

    def test_create_task(self):
        url = reverse('create_task')
        data = {
            'name': 'New Task',
            'description': 'New task description',
            'to_be_completed_time': '2024-08-01T10:00:00Z'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_create_task_missing_fields(self):
        url = reverse('create_task')
        data = {
            'name': 'New Task'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_task(self):
        url = reverse('update_task', args=[self.task.id])
        data = {
            'name': 'Updated Task',
            'description': 'Updated description',
            'to_be_completed_time': '2024-09-01T10:00:00Z'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Updated Task')
        self.assertEqual(self.task.description, 'Updated description')

    def test_update_task_invalid_user(self):
        other_user = User.objects.create_user(username='otheruser', password='password', email='other@example.com')
        other_task = Task.objects.create(
            user=other_user,
            name='Other Task',
            description='Other description',
            to_be_completed_time='2024-08-01T10:00:00Z'
        )
        url = reverse('update_task', args=[other_task.id])
        data = {
            'name': 'Updated Task'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_task_completed(self):
        url = reverse('mark_task_completed', args=[self.task.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)
        self.assertIsNotNone(self.task.completion_time)

    def test_mark_task_already_completed(self):
        self.task.completed = True
        self.task.completion_time = timezone.now()
        self.task.save()
        url = reverse('mark_task_completed', args=[self.task.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Task is already completed')

    def test_soft_delete_task(self):
        url = reverse('soft_delete_task', args=[self.task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertTrue(self.task.deleted)

    def test_list_tasks(self):
        url = reverse('list_tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)