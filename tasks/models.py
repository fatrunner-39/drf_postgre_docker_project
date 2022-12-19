from django.db import models
from users.models import User


class TaskType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    creator_id = models.ForeignKey(User, on_delete=models.CASCADE)
    type_id = models.ForeignKey(TaskType, null=True, on_delete=models.SET_NULL)
    content = models.TextField()


class TasksToRunners(models.Model):
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)
    runner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    notes = models.CharField(max_length=200, null=True)
