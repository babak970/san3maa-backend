from rest_framework.permissions import BasePermission


class IsArenaOwnerOrAdmin(BasePermission):
    """
    Object-level permission:
    - superuser can do anything
    - owner can edit their own Arena / Court
    """
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_superuser:
            return True

        # obj can be Arena or Court
        owner_id = None

        if hasattr(obj, "owner_id"):  # Arena
            owner_id = obj.owner_id
        elif hasattr(obj, "arena") and hasattr(obj.arena, "owner_id"):  # Court
            owner_id = obj.arena.owner_id

        return request.user and request.user.is_authenticated and owner_id == request.user.id
