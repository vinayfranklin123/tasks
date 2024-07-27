from rest_framework import serializers
from .models import Task
from django.utils import timezone

class TaskSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'to_be_completed_time', 'created_at', 'updated_at', 'completed', 'completion_time', 'user', 'deleted', 'deleted_at', 'status']
        read_only_fields = ['created_at', 'updated_at', 'user', 'completed', 'completion_time', 'deleted', 'deleted_at']

    def get_status(self, obj):
        now = timezone.now()
        if obj.completed:
            return 'completed'
        elif obj.to_be_completed_time < now:
            return 'delayed'
        else:
            return 'pending'
