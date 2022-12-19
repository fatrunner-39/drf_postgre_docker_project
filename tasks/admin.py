from django.contrib import admin
from .models import TaskType, Task

admin.site.register(TaskType)
admin.site.register(Task)
