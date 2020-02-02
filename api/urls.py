from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('log', UserLogViewSet)
router.register('court', CourtViewSet)
router.register('document', DocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
