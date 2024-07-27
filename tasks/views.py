import json
import logging
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import models
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer

# Create a logger instance
logger = logging.getLogger('myapp')

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    logger.info('Registering user: %s', username)

    if not username or not password or not email:
        logger.error('Missing required fields during registration')
        return Response({'error': 'Please provide all required fields'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        logger.warning('Username %s already exists', username)
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    logger.info('User %s created successfully', username)
    return Response({'message': 'User created successfully'})

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username')
    password = data.get('password')

    logger.info('Attempting to log in user: %s', username)

    if not username or not password:
        logger.error('Missing username or password during login')
        return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        logger.info('User %s logged in successfully', username)
        return Response({'token': token.key})
    else:
        logger.error('Invalid credentials for user: %s', username)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logger.info('User %s logging out', request.user.username)
    request.user.auth_token.delete()
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    data = json.loads(request.body.decode('utf-8'))
    serializer = TaskSerializer(data=data)

    to_be_completed_time_str = data['to_be_completed_time'].rstrip('Z')
    try:
        to_be_completed_time = timezone.datetime.fromisoformat(to_be_completed_time_str)
        to_be_completed_time = timezone.make_aware(to_be_completed_time, timezone.get_default_timezone())
    except ValueError:
        return Response({'error': 'Invalid datetime format.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if to_be_completed_time < timezone.now():
        return Response({'error': 'to_be_completed_time cannot be in the past.'}, status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        task = serializer.save(user=request.user)
        logger.info('Task created successfully by user %s', request.user.username)
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
    
    logger.error('Error creating task for user %s: %s', request.user.username, serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, deleted=False)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    if task.user != request.user:
        return Response({'error': 'You do not have permission to edit this task'}, status=status.HTTP_403_FORBIDDEN)

    data = json.loads(request.body.decode('utf-8'))

    if 'to_be_completed_time' in data:
        to_be_completed_time_str = data['to_be_completed_time'].rstrip('Z')
        try:
            to_be_completed_time = timezone.datetime.fromisoformat(to_be_completed_time_str)
            if to_be_completed_time.tzinfo is None:
                to_be_completed_time = timezone.make_aware(to_be_completed_time, timezone.get_default_timezone())
        except ValueError:
            return Response({'error': 'Invalid datetime format.'}, status=status.HTTP_400_BAD_REQUEST)

        if to_be_completed_time < timezone.now():
            return Response({'error': 'to_be_completed_time cannot be in the past.'}, status=status.HTTP_400_BAD_REQUEST)
        
    serializer = TaskSerializer(task, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        logger.info('Task updated successfully by user %s', request.user.username)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    logger.error('Error updating task for user %s: %s', request.user.username, serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_task_completed(request, task_id):
    try:
        task = Task.objects.get(id=task_id, deleted=False)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    if task.user != request.user:
        return Response({'error': 'You do not have permission to edit this task'}, status=status.HTTP_403_FORBIDDEN)

    if task.completed:
        return Response({'message': 'Task is already completed', 'completion_time': task.completion_time}, status=status.HTTP_200_OK)

    task.completed = True
    task.completion_time = timezone.now()
    task.save()

    logger.info('Task marked as completed by user %s', request.user.username)
    return Response({'message': 'Task marked as completed', 'completion_time': task.completion_time}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def soft_delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, deleted=False)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    if task.user != request.user:
        return Response({'error': 'You do not have permission to edit this task'}, status=status.HTTP_403_FORBIDDEN)

    task.deleted = True
    task.deleted_at = timezone.now()
    task.save()

    logger.info('Task soft-deleted by user %s', request.user.username)
    return Response({'message': 'Task marked as deleted'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_tasks(request):
    sort_by = request.query_params.get('sort_by', 'created_at')
    show_pending = request.query_params.get('show_pending', 'false').lower() == 'true'
    show_completed = request.query_params.get('show_completed', 'false').lower() == 'true'
    valid_sort_fields = ['created_at', 'to_be_completed_time', 'completion_time']

    if sort_by not in valid_sort_fields:
        return Response({'error': f'Invalid sort_by value. Valid values are {valid_sort_fields}'}, status=status.HTTP_400_BAD_REQUEST)

    tasks = Task.objects.filter(user=request.user, deleted=False)

    if show_pending:
        tasks = tasks.filter(completed=False)
    elif show_completed:
        tasks = tasks.filter(completed=True)

    if sort_by == 'completion_time':
        tasks = tasks.annotate(
            sort_priority = models.Case(
                models.When(completion_time__isnull=False, then=0),
                models.When(completion_time__isnull=True, then=1),
                default=2,
                output_field=models.IntegerField(),
            ),
            sort_field = models.Case(
                models.When(completion_time__isnull=True, then='to_be_completed_time'),
                default='completion_time',
                output_field=models.DateTimeField(),
            )
        ).order_by('sort_priority', '-sort_field')
    elif sort_by == 'to_be_completed_time':
        tasks = tasks.order_by(f'-{sort_by}')
    else:
        tasks = tasks.order_by(f'-{sort_by}')

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
