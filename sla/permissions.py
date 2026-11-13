from rest_framework.permissions import BasePermission, SAFE_METHODS


class SLAPolicyPermission(BasePermission):
    """
    Control access to SLA policies by role and organization.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Authenticated users can view SLA policies.
        if request.method in SAFE_METHODS:
            return True

        # Only superusers, ADMIN and MANAGER can manage SLA policies.
        return user.is_superuser or user.role in ["ADMIN", "MANAGER"]

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Superusers can access all organizations.
        if user.is_superuser:
            return True

        # All other users are restricted to their own organization.
        return obj.organization_id == user.organization_id