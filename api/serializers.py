from rest_framework import serializers
from .models import *


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('review', 'score')


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ('desc', 'timestamp',)


class UserSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',)


class UserLogSerializer(serializers.ModelSerializer):
    logs = LogSerializer(many=True)

    class Meta:
        model = User
        fields = ('username', 'logs',)


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('url', 'timestamp',)


class ExtendedUserSerializer(serializers.HyperlinkedModelSerializer):
    ban_list = UserSerializer(many=True)
    username = serializers.CharField(
        source='base_user.username'
    )
    first_name = serializers.CharField(
        source='base_user.first_name'
    )
    last_name = serializers.CharField(
        source='base_user.last_name'
    )
    email = serializers.CharField(
        source='base_user.email'
    )
    is_staff = serializers.BooleanField(
        source='base_user.is_staff'
    )
    reviews = ReviewSerializer(
        source='base_user.reviews', many=True
    )
    documents = DocumentSerializer(
        source='base_user.documents', many=True
    )

    class Meta:
        model = ExtendedUser
        fields = ('username', 'first_name', 'last_name',
                  'email', 'ban_list', 'is_verified',
                  'phone_number', 'credit', 'is_staff',
                  'reviews', 'documents', )


class RacketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Racket
        fields = ('name', 'price', 'count',)


class ShuttlecockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shuttlecock
        fields = ('name', 'count_per_unit', 'count',)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('url', 'timestamp')


class CourtSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False)
    images = ImageSerializer(many=True)

    class Meta:
        model = Court
        fields = ('id', 'name', 'price', 'owner', 'desc',
                  'rating_count', 'avg_score', 'images',)


class UserDocumentSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True)

    class Meta:
        model = User
        fields = ('username', 'documents')
