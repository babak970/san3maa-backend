# arenas/urls.py
from rest_framework.routers import DefaultRouter
from .views import ArenaViewSet, CourtViewSet

router = DefaultRouter()
router.register('arenas', ArenaViewSet, basename='arena')
router.register('courts', CourtViewSet, basename='court')

urlpatterns = router.urls
