# arenas/views.py
from rest_framework import viewsets, permissions
from .models import Arena, Court
from .serializers import ArenaSerializer, CourtSerializer


class ArenaViewSet(viewsets.ModelViewSet):
    queryset = Arena.objects.all()
    serializer_class = ArenaSerializer

    def get_permissions(self):
        # Read-only (GET, HEAD, OPTIONS) → allow anyone
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        # Write operations (POST, PUT, PATCH, DELETE) → must be logged in
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # When someone creates an arena via API, owner = current user
        serializer.save(owner=self.request.user)


class CourtViewSet(viewsets.ModelViewSet):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
