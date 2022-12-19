from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Comment
from .serializers import CommentSerializer
from users.permissions import IsOwnerOrAdminOrReadOnly


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_id']

    def create(self, request, *args, **kwargs):
        data = request.data
        data['from_user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

