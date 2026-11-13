
from datetime import timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated

from sla.models import SLAPolicy
from .models import Ticket
from .serializers import TicketSerializer
from .permissions import TicketRolePermission


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.none()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, TicketRolePermission]

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

        if user.is_superuser:
            return Ticket.objects.select_related(
                "organization",
                "created_by",
                "assigned_to",
            ).all()

        if user.organization_id:
            return Ticket.objects.select_related(
                "organization",
                "created_by",
                "assigned_to",
            ).filter(organization_id=user.organization_id)

        return Ticket.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        organization = serializer.validated_data["organization"]

        if not user.is_superuser:
            if not user.organization_id:
                raise PermissionDenied(
                    "You must belong to an organization to create a ticket."
                )

            if organization.id != user.organization_id:
                raise PermissionDenied(
                    "You can create tickets only for your own organization."
                )

        priority = serializer.validated_data.get(
            "priority",
            Ticket.Priority.MEDIUM,
        )

        sla_policy = SLAPolicy.objects.filter(
            organization=organization,
            priority=priority,
            is_active=True,
        ).first()

        if sla_policy:
            now = timezone.now()

            response_deadline = now + timedelta(
                minutes=sla_policy.response_time_minutes
            )

            resolution_deadline = now + timedelta(
                minutes=sla_policy.resolution_time_minutes
            )

            serializer.save(
                created_by=user,
                response_deadline=response_deadline,
                resolution_deadline=resolution_deadline,
            )
        else:
            serializer.save(created_by=user)


    def perform_update(self, serializer):
        ticket = self.get_object()

        old_status = ticket.status
        new_status = serializer.validated_data.get(
            "status",
            old_status,
        )

        now = timezone.now()
        update_fields = {}

        # Record the first response only once.
        if (
            old_status != Ticket.Status.IN_PROGRESS
            and new_status == Ticket.Status.IN_PROGRESS
            and ticket.first_responded_at is None
        ):
            update_fields["first_responded_at"] = now

        # Record the latest resolution time on every new resolution.
        if (
            old_status != Ticket.Status.RESOLVED
            and new_status == Ticket.Status.RESOLVED
        ):
            update_fields["resolved_at"] = now

        serializer.save(**update_fields)
