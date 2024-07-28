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