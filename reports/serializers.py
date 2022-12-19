from rest_framework import serializers
from .models import Visibility, Report, ImageLoader


class VisibilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Visibility
        fields = ('id', 'name')


class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        fields = '__all__'


class ImageLoaderSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageLoader
        fields = '__all__'
