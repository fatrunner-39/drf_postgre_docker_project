from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import User, Role, CoachToRunner, Subscribe


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'role_id', 'is_active', 'bio', 'img')

    def validate_password(self, value: str) -> str:
        """
        Hash value passed by user.

        :param value: password of a user
        :return: a hashed version of the password
        """
        return make_password(value)


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ('id', 'name')


class CoachToRunnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = CoachToRunner
        fields = ('coach_id', 'runner_id')


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('subscriber_id', 'user_id')
