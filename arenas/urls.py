# arenas/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ArenaViewSet, CourtViewSet
from .api import AvailabilityBlocksView

router = DefaultRouter()
router.register('arenas', ArenaViewSet, basename='arena')
router.register('courts', CourtViewSet, basename='court')

urlpatterns = [
    path('availability/blocks/', AvailabilityBlocksView.as_view()),
] + router.urls
