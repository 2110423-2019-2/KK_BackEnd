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


class RacketBookingSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(
        source='racket.name'
    )

    class Meta:
        model = RacketBooking
        fields = ('id', 'name', 'price')


class ShuttlecockBookingSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(
        source='shuttlecock.name'
    )
    count_per_unit = serializers.CharField(
        source='shuttlecock.count_per_unit'
    )

    class Meta:
        model = ShuttlecockBooking
        fields = ('id', 'name', 'price', 'count', 'count_per_unit')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('url', 'timestamp')


class CourtSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False)
    images = ImageSerializer(many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Court
        fields = ('id', 'name', 'price', 'owner', 'desc',
                  'rating_count', 'avg_score', 'reviews', 'images', 'court_count', 'is_verified', 'lat', 'long')


class BookingSerializer(serializers.ModelSerializer):
    court = CourtSerializer(many=False)

    class Meta:
        model = Booking
        fields = ('id', 'day_of_the_week', 'court', 'court_number', 'is_active', 'price',
                  'start', 'end', 'racket_bookings', 'shuttlecock_bookings')


class RacketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Racket
        fields = ('id', 'name', 'price' )


class ShuttlecockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shuttlecock
        fields = ('id', 'name', 'count_per_unit', 'count')


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
    bookings = BookingSerializer(
        source='base_user.bookings', many=True
    )

    class Meta:
        model = ExtendedUser
        fields = ('username', 'first_name', 'last_name',
                  'email', 'ban_list', 'is_verified',
                  'phone_number', 'credit', 'is_staff',
                  'reviews', 'documents', 'bookings',)


class UserDocumentSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True)

    class Meta:
        model = User
        fields = ('username', 'documents')
