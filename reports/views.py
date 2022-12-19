import datetime
import os
from urllib.parse import urljoin
from django.db.models import Q

from django.conf import settings
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters, mixins, generics
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Visibility, Report, ImageLoader
from .serializers import VisibilitySerializer, ReportSerializer, ImageLoaderSerializer
from users.permissions import IsAdminOrReadOnly, IsCoach, check_role
from users.models import Subscribe, CoachToRunner


def get_subscribes(request):
    return [sub.user_id_id for sub in Subscribe.objects.filter(subscriber_id=request.user.id)]


def get_runners_groups(request):
    return [sub.runner_id_id for sub in CoachToRunner.objects.filter(coach_id=request.user.id)]


class VisibilityViewSet(viewsets.ModelViewSet):
    queryset = Visibility.objects.all()
    serializer_class = VisibilitySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def destroy(self, request, *args, **kwargs):
        visibility_id = self.get_object().id
        super(VisibilityViewSet, self).destroy(request, *args, **kwargs)
        return Response(data={"success": f"Visible status with id = {visibility_id} was deleted"})


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task_id', 'runner_id']

    def create(self, request, *args, **kwargs):
        data = request.data
        if not data.get('started_at'):
            data['started_at'] = datetime.datetime.now()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # remove file
        [image.file.delete() for image in ImageLoader.objects.filter(report_id=instance.id)]
        instance.file_id.file.delete()

        report_id = instance.id
        # check report owner or superadmin
        if not check_role.is_report_owner_or_admin(request, instance):
            return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(data={'result': f'report with id = {report_id} success deleted'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # check report owner or superadmin
        if not check_role.is_report_owner_or_admin(request, instance):
            return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.visible_id.name == 'Закрытая':
            if not check_role.is_owner_or_admin(request, instance):
                return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
            coach_runners = [runner.id for runner in CoachToRunner.objects.filter(coach_id=request.user.id)]
            if request.user.role_id.name == 'coach' and instance.runner_id.id not in coach_runners:
                return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if instance.visible_id.name == 'Только для подписчиков':
            if instance.runner_id.id != request.user.id and (instance.runner_id.id not in get_subscribes(request)):
                return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.user.role_id.name == 'superadmin':
            queryset = queryset
        elif request.user.role_id.name == 'runner':
            queryset = queryset.filter(Q(visible_id=Visibility.objects.get(name='Видимая для всех')) |
                                            Q(runner_id=request.user.id) |
                                            Q(visible_id=Visibility.objects.get(name='Только для подписчиков'),
                                              runner_id__in=get_subscribes(request))).\
                filter(runner_id__in=get_subscribes(request))
        else:
            queryset = queryset.filter(Q(visible_id=Visibility.objects.get(name='Видимая для всех')) |
                                            Q(runner_id=request.user.id) |
                                            Q(visible_id=Visibility.objects.get(name='Только для подписчиков'),
                                              runner_id__in=get_subscribes(request)) |
                                            Q(visible_id=Visibility.objects.get(name='Закрытая'),
                                              runner_id__in=get_runners_groups(request))).\
                filter(runner_id__in=get_subscribes(request))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CoachReportsView(generics.ListAPIView):
    queryset = Report.objects
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        if not check_role.is_coach(request):
            return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        coach_runners = [runner.id for runner in CoachToRunner.objects.filter(coach_id=request.user.id)]
        queryset = self.queryset.filter(runner_id__in=coach_runners)
        # queryset = self.queryset.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ImageView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        all_images = ImageLoader.objects.all()
        serializer = ImageLoaderSerializer(all_images, many=True)
        instances = [dict(obj) for obj in serializer.data]
        for instance in instances:
            instance['file'] = urljoin(settings.ABSOLUTE_URL, instance['file'])
        return JsonResponse(instances, safe=False)

    def post(self, request, *args, **kwargs):

        # converts querydict to original dict
        images = dict((request.data).lists())['files']
        instances = []
        for img in images:
            modified_data = {
                'file': img,
                'report_id': request.data['report_id']
            }
            file_serializer = ImageLoaderSerializer(data=modified_data)
            if file_serializer.is_valid():
                file_serializer.save()
                instances.append(file_serializer.data)
            else:
                return Response(data={"error": "Invalid file"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(instances, status=status.HTTP_201_CREATED)


class RetrieveDestroyImageView(generics.RetrieveDestroyAPIView):
    queryset = ImageLoader.objects.all()
    serializer_class = ImageLoaderSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id = instance.id
        owner = instance.report_id.runner_id.id
        if owner != request.user.id or request.user.role_id.name != 'superadmin':
            return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()

        return Response(data=f'Image with id = {instance_id} was deleted')
