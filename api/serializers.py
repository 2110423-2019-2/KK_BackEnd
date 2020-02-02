from rest_framework import serializers
from .models import *


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('review', 'score')


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ('desc', 'timestamp', )


class UserSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'is_staff', 'reviews', 'documents', )


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
        fields = ('base_user', 'ban_list', 'is_verified', 'phone_number', )


class RacketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Racket
        fields = ('name', 'price', 'count', )


class ShuttlecockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shuttlecock
        fields = ('name', 'count_per_unit', 'count', )


class CourtSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False)

    class Meta:
        model = Court
        fields = ('id', 'name', 'price', 'owner', 'desc',
                  'rating_count', 'avg_score', 'images', )


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('url', 'timestamp', )
