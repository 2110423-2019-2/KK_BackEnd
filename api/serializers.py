from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ExtendedUser, Court, Log


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ('id', 'desc', )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', )


class UserLogSerializer(serializers.ModelSerializer):
    logs = LogSerializer(many=True)

    class Meta:
        model = User
        fields = ('username', 'logs', )


class ExtendedUserSerializer(serializers.ModelSerializer):
    base_user = UserSerializer(many=False)
    ban_list = UserSerializer(many=True)

    class Meta:
        model = ExtendedUser
        fields = ('id', 'base_user', 'ban_list', )


class CourtSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False)

    class Meta:
        model = Court
        field = ('id', 'name', 'owner', )

