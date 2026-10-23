
from rest_framework.permissions import BasePermission, SAFE_METHODS


class TicketRolePermission(BasePermission):
    """
    Apply role-based permissions to ticket actions.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow read-only requests for authenticated users.
        if request.method in SAFE_METHODS:
            return True

        # Superusers can perform all ticket actions.
        if request.user.is_superuser:
            return True

        role = request.user.role

        # Only ADMIN and MANAGER can delete tickets.
        if view.action == "destroy":
            return role == "ADMIN"

        # Only ADMIN, MANAGER, and AGENT can update tickets.
        if view.action in ["update", "partial_update"]:
            return role in ["ADMIN", "MANAGER", "AGENT"]

        # Authenticated users can create tickets.
        if view.action == "create":
            return role in ["ADMIN", "MANAGER", "AGENT", "CUSTOMER"]

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or user.role == "ADMIN":
            return True

        if request.method in SAFE_METHODS:
            return obj.organization_id == user.organization_id

        if view.action in ["update", "partial_update"]:
            if user.role == "MANAGER":
                return obj.organization_id == user.organization_id

            if user.role == "AGENT":
                return obj.assigned_to_id == user.id

            if user.role == "CUSTOMER":
                return obj.created_by_id == user.id

        return False
