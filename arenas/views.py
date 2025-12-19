from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Arena, Court
from .serializers import ArenaSerializer, CourtSerializer
from .permissions import IsArenaOwnerOrAdmin


class ArenaViewSet(viewsets.ModelViewSet):
    queryset = Arena.objects.all()
    serializer_class = ArenaSerializer

    def get_permissions(self):
        # Read = public
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]

        # Write = must be logged in + must be owner (object-level)
        return [permissions.IsAuthenticated(), IsArenaOwnerOrAdmin()]

    def perform_create(self, serializer):
        # Owner becomes the logged-in user automatically
        serializer.save(owner=self.request.user)


class CourtViewSet(viewsets.ModelViewSet):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer

    def get_permissions(self):
        # Read = public
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]

        # Write = must be logged in + must be owner (object-level)
        return [permissions.IsAuthenticated(), IsArenaOwnerOrAdmin()]

    def perform_create(self, serializer):
        # Extra check: you can only create a court for YOUR arena
        arena = serializer.validated_data["arena"]
        if arena.owner_id != self.request.user.id and not self.request.user.is_superuser:
            raise PermissionDenied("You can only add courts to your own arenas.")
        serializer.save()
