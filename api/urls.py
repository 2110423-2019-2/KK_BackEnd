from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import *

router = routers.SimpleRouter()
router.register('user', UserViewSet)
router.register('log', LogViewSet)
router.register('court', CourtViewSet)
router.register('document', DocumentViewSet)
router.register('booking', BookingViewSet)
router.register('shuttlecock', ShuttlecockViewSet)
router.register('racket', RacketViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('speech/', Speech.as_view()),
]
