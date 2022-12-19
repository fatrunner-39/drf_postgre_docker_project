from rest_framework import serializers
from .models import TaskType, Task, TasksToRunners


class TaskTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskType
        fields = ('id', 'name')


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'creator_id', 'type_id', 'content')


class TasksToRunnersSerializer(serializers.ModelSerializer):

    class Meta:
        model = TasksToRunners
        fields = ('task_id', 'runner_id', 'date', 'notes')
