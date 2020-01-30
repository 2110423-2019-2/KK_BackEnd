from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import ExtendedUserViewSet, UserLogViewSet

router = routers.DefaultRouter()
router.register('users', ExtendedUserViewSet)
router.register('userlog', UserLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
