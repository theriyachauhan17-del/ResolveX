from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Ticket
from .serializers import TicketSerializer
from .permissions import TicketRolePermission


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.none()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, TicketRolePermission]

    # Filtering, searching, and ordering
    filter_backends = [
    DjangoFilterBackend,
    SearchFilter,
    OrderingFilter,
    ]

    filterset_fields = ["status", "priority"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "priority", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        # Only Django superusers can access all organizations.
        if user.is_superuser:
            return Ticket.objects.select_related(
                "organization",
                "created_by",
                "assigned_to",
            ).all()

        # All other users can see tickets from their own organization.
        if user.organization_id:
            return Ticket.objects.select_related(
                "organization",
                "created_by",
                "assigned_to",
            ).filter(organization_id=user.organization_id)

        # Users without an organization see no tickets.
        return Ticket.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        # Superusers can create tickets for any organization.
        if user.is_superuser:
            serializer.save(created_by=user)
            return

        # Regular users must belong to an organization.
        if not user.organization_id:
            raise PermissionDenied(
                "You must belong to an organization to create a ticket."
            )

        # Regular users can create tickets only for their organization.
        if (
            serializer.validated_data["organization"].id
            != user.organization_id
        ):
            raise PermissionDenied(
                "You can create tickets only for your own organization."
            )

        serializer.save(created_by=user)
