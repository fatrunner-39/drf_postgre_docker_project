import datetime
import json

from django.db import models
from users.models import User
from loaders.models import FileLoader
from tasks.models import Task


class Visibility(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Report(models.Model):
    title = models.CharField(max_length=150)
    runner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    visible_id = models.ForeignKey(Visibility, on_delete=models.CASCADE)
    file_id = models.ForeignKey(FileLoader, null=True, on_delete=models.CASCADE)
    task_id = models.ForeignKey(Task, null=True, on_delete=models.CASCADE)
    distance = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    moving_time = models.DecimalField(max_digits=6, decimal_places=2)
    avg_pace = models.CharField(max_length=50, null=True)
    started_at = models.DateTimeField()
    description = models.TextField(null=True)


class ImageLoader(models.Model):
    file = models.ImageField(upload_to='reports/%Y_%m_%d/')
    report_id = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='images')
