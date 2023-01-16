from django.db.models.functions import Concat
from django.db.models import Value as V
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from loguru import logger

from .models import User, Role, CoachToRunner, Subscribe
from .serializers import UserSerializer, RoleSerializer, CoachToRunnerSerializer, SubscribeSerializer
from .permissions import IsAdminOrReadOnly, IsCoach, check_role
from send_mail import user_greeting
from .celery_tasks import send_email_task


class CreateUserView(mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    queryset = User.objects
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        new_user = super().create(request, *args, **kwargs)
        user = new_user.data
        full_name = f'{user["first_name"]}{user["last_name"]}'
        message = user_greeting(full_name)
        send_email_task(
            title='Greeting',
            message=message,
            to_emails=user["username"]
        )
        logger.info(f'User with username = {user["username"]} was registered success!')
        return new_user


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not check_role.is_owner_or_admin(request, instance):
            return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        user_id = instance.id
        super(UserViewSet, self).destroy(request, *args, **kwargs)
        logger.info(f'User with id = {user_id} was deleted')
        return Response(data={"success": f"User with id = {user_id} was deleted"})

    def list(self, request, *args, **kwargs):
        query = request.query_params.get('fullname')
        if query:
            queryset = self.queryset.annotate(full_name=Concat('first_name', V(' '), 'last_name')).\
                filter(full_name__icontains=query)
        else:
            queryset = self.queryset

        if not request.user.is_staff:
            if check_role.is_coach(request):
                instances = CoachToRunner.objects.filter(coach_id=request.user.id)
                instances = [instance.runner_id.id for instance in instances]
                queryset = self.queryset.filter(id__in=instances)
            else:
                return Response(data={"error": f"Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        else:
            queryset = queryset.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if not check_role.is_owner_or_admin(request, instance):
            return Response(data={"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']

    def destroy(self, request, *args, **kwargs):
        role_id = self.get_object().id
        super(RoleViewSet, self).destroy(request, *args, **kwargs)
        return Response(data={"success": f"Role with id = {role_id} was deleted"})


class CoachToRunnerViewSet(viewsets.ModelViewSet):
    queryset = CoachToRunner.objects
    serializer_class = CoachToRunnerSerializer
    permission_classes = [IsAuthenticated, IsCoach]

    def create(self, request, *args, **kwargs):
        data = request.data
        for runner_id in data['runner_ids']:
            query = self.queryset.filter(coach_id=request.user.id, runner_id=runner_id).first()
            if query:
                return Response(data={"error": "Instance already exists"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(data={
                'coach_id': request.user.id,
                'runner_id': runner_id
            })
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        return Response(data={"success": f"Users with ids = {data['runner_ids']} added to "
                                         f"coach with id = {request.user.id}"})

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        print(serializer.data)
        queryset = [obj['runner_id'] for obj in serializer.data]
        return Response(queryset)

    @action(methods=["DELETE"], detail=False)
    def delete(self, request):
        data = request.data
        query = self.queryset.filter(coach_id=request.user.id, runner_id__in=data['runner_ids'])
        if not query:
            return Response(data={"error": "Noting to delete"}, status=status.HTTP_400_BAD_REQUEST)
        query.delete()
        return Response(data={"success": f"Users with ids = {data['runner_ids']} deleted from "
                                         f"coach with id = {request.user.id}"})


class SubscribeViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    queryset = Subscribe.objects
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        request.data['subscriber_id'] = request.user.id
        return super(SubscribeViewSet, self).create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if not check_role.is_admin(request):
            queryset = self.queryset.filter(subscriber_id=request.user.id)
        else:
            queryset = self.queryset.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["DELETE"], detail=False)
    def delete(self, request):
        data = request.data
        self.queryset.get(subscriber_id=request.user.id, user_id=data['user_id']).delete()
        return Response(data={"success": f"You have unsubscribed from user_id = {data['user_id']}"})


