from rest_framework import serializers
from .models import job
from django.contrib.auth.models import User
from django_celery_results.models import TaskResult


class jobserializer(serializers.ModelSerializer):  # create class to serializer model
    creator = serializers.ReadOnlyField(source='creator.username')
    resultid=serializers.ReadOnlyField(source='resultid.task_id')

    class Meta:
        model = job
        fields = ('id', 'hash',  'creator', 'resultid')


class UserSerializer(serializers.ModelSerializer):  # create class to serializer usermodel
    jobs = serializers.PrimaryKeyRelatedField(many=True, queryset=job.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'jobs')


class TaskResultserializer(serializers.ModelSerializer):  # create class to serializer model
    user_name = serializers.SerializerMethodField()

    def __init__(self,qs):
        super().__init__(self,qs)
        self.username=None

    def get_user_name(self,obj):
        """getter method to add field retrieved_time"""
        return self.username

    class Meta:
        model = TaskResult
        fields = ('task_id', 'status',  'result','user_name')
