import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import TaskType, Task, TasksToRunners
from .serializers import TaskTypeSerializer, TaskSerializer, TasksToRunnersSerializer
from users.permissions import IsCoach, check_role


class TaskTypeViewSet(viewsets.ModelViewSet):
    queryset = TaskType.objects.all()
    serializer_class = TaskTypeSerializer
    permission_classes = [IsAuthenticated, IsCoach]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def destroy(self, request, *args, **kwargs):
        task_id = self.get_object().id
        super(TaskTypeViewSet, self).destroy(request, *args, **kwargs)
        return Response(data={"success": f"Task's type with id = {task_id} was deleted"})


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        creator = request.user
        if not creator.role_id.name in ('admin', 'coach'):
            return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        data['creator_id'] = creator.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        task_type = request.query_params.get('type')
        if task_type:
            task_types = TaskType.objects.filter(name__icontains=task_type).all()
            type_ids = [task_type.id for task_type in task_types]
            queryset = self.queryset.filter(type_id__in=type_ids)
        else:
            queryset = self.queryset
        user = request.user
        if user.role_id.name == 'runner':
            runner_tasks = TasksToRunners.objects.filter(runner_id=user.id)
            runner_tasks_ids = [task.task_id.id for task in runner_tasks]
            queryset = queryset.filter(id__in=runner_tasks_ids)
        elif user.role_id.name == 'coach':
            queryset = queryset.filter(creator_id=user.id)
        else:
            queryset = queryset.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()

        if check_role.is_coach(request):
            if request.user.id != instance.creator_id.id:
                return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if not check_role.is_coach_or_admin(request):
            runner_tasks = TasksToRunners.objects.filter(runner_id=request.user.id)
            tasks_ids = [run_task.task_id_id for run_task in runner_tasks]
            if instance.id not in tasks_ids:
                return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if not check_role.is_coach_or_admin(request):
            return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return super(TaskViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        task_id = instance.id
        if check_role.is_coach(request):
            if request.user.id != instance.creator_id.id:
                return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if not check_role.is_coach_or_admin(request):
            return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({"success": f"Task with id = {task_id} was deleted"})


class TasksToRunnersView(viewsets.ModelViewSet):
    queryset = TasksToRunners.objects
    serializer_class = TasksToRunnersSerializer
    permission_classes = [IsAuthenticated, IsCoach]

    def create(self, request, *args, **kwargs):
        data = request.data

        for runner_id in data['runners_ids']:
            create_data = {
                "task_id": data.get('task_id', None),
                "runner_id": runner_id,
                "date": data.get('date', datetime.date.today()),
                "notes": data.get('notes', None)
            }
            serializer = self.get_serializer(data=create_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        return Response(data={"result": "success"}, status=status.HTTP_201_CREATED)

    @action(methods=["DELETE"], detail=False)
    def delete(self, request):
        data = request.data
        tasks = Task.objects.filter(creator_id=request.user.id)
        tasks = [task.id for task in tasks]
        if data['task_id'] not in tasks:
            return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        query = self.queryset.filter(task_id=data['task_id'], runner_id=data['runner_id'], date=data['date'])
        if data.get('notes'):
            query = query.filter(notes=data.get('notes'))
        if not query:
            return Response(data={"error": "Noting to delete"}, status=status.HTTP_400_BAD_REQUEST)
        query.delete()
        return Response(data={"success": f"Task with id = {data['task_id']} deleted from "
                                         f"runner with id = {data['runner_id']}"})
