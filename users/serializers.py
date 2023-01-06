from rest_framework import serializers
from .models import User, Role, CoachToRunner, Subscribe


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'role_id', 'is_active', 'bio', 'img')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        runner_id = Role.objects.get(name='runner')
        if not validated_data.get('role_id'):
            validated_data['role_id'] = runner_id
        user = User(
            username=validated_data['username'],
            first_name=validated_data['first_name'] if validated_data.get('first_name') else '',
            last_name=validated_data['last_name'] if validated_data.get('last_name') else '',
            role_id=validated_data['role_id'],
            is_active=True,
            bio=validated_data['bio'] if validated_data.get('bio') else '',
            img=validated_data['img'] if validated_data.get('img') else '',
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


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
