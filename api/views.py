from rest_framework import viewsets
from .models import ExtendedUser
from .serializers import ExtendedUserSerializer, UserLogSerializer
from django.contrib.auth.models import User


class ExtendedUserViewSet(viewsets.ModelViewSet):
    queryset = ExtendedUser.objects.all()
    serializer_class = ExtendedUserSerializer


class UserLogViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserLogSerializer

