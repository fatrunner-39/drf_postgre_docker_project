from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskTypeViewSet, TasksToRunnersView, TaskViewSet

router = DefaultRouter()

router.register('task_types', TaskTypeViewSet)
router.register('tasks', TaskViewSet)
router.register('tasks/runners', TasksToRunnersView)

urlpatterns = [
    path('', include(router.urls)),
]
