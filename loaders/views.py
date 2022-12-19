
import gpxpy
import gpxpy.gpx

from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import FileLoader
from .serializers import FileLoaderSerializer
from reports.models import Report, Visibility
from users.permissions import IsAdminOrReadOnly, IsCoach, check_role


class FileLoaderViewSet(viewsets.ModelViewSet):
    queryset = FileLoader.objects.all()
    serializer_class = FileLoaderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        gpx = gpxpy.parse(request.data['file'])

        # save gpx file
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # Save report
        distance = round(gpx.get_moving_data().moving_distance)
        moving_time = gpx.get_moving_data().moving_time
        minutes = round((moving_time/60)//(distance/1000))
        seconds = round((moving_time/60)%(distance/1000)/(distance/1000)*60)
        if seconds in list(range(0, 10)):
            seconds = f'0{seconds}'
        avg_pace = f'{minutes}:{seconds} min/km'
        closed = Visibility.objects.get(name='Закрытая')
        file_id = FileLoader.objects.get(id=serializer.data['id'])
        # create report
        Report.objects.create(
            title='Running',
            file_id=file_id,
            runner_id=request.user,
            visible_id=closed,
            distance=distance,
            moving_time=moving_time,
            avg_pace=avg_pace,
            started_at=gpx.get_time_bounds().start_time
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

