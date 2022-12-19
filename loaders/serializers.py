from rest_framework import serializers
from .models import FileLoader


class FileLoaderSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileLoader
        fields = ('id', 'file')
