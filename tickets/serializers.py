
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    assigned_to_username = serializers.CharField(
        source="assigned_to.username",
        read_only=True,
        allow_null=True,
    )

    response_sla_status = serializers.SerializerMethodField()
    resolution_sla_status = serializers.SerializerMethodField()

    class Meta:
        model = Ticket

        fields = [
            "id",
            "organization",
            "organization_name",
            "title",
            "description",
            "priority",
            "status",
            "created_by",
            "created_by_username",
            "assigned_to",
            "assigned_to_username",
            "created_at",
            "updated_at",
            "response_deadline",
            "resolution_deadline",
            "first_responded_at",
            "resolved_at",
            "response_sla_status",
            "resolution_sla_status",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "response_deadline",
            "resolution_deadline",
            "first_responded_at",
            "resolved_at",
            "response_sla_status",
            "resolution_sla_status",
        ]

    def get_response_sla_status(self, obj):
        if not obj.response_deadline:
            return "NOT_CONFIGURED"

        if obj.first_responded_at:
            if obj.first_responded_at <= obj.response_deadline:
                return "COMPLETED_ON_TIME"

            return "COMPLETED_LATE"

        if timezone.now() > obj.response_deadline:
            return "BREACHED"

        return "ON_TRACK"

    def get_resolution_sla_status(self, obj):
        if not obj.resolution_deadline:
            return "NOT_CONFIGURED"

        if obj.status in [
            Ticket.Status.RESOLVED,
            Ticket.Status.CLOSED,
        ]:
            if not obj.resolved_at:
                return "ON_TRACK"

            if obj.resolved_at <= obj.resolution_deadline:
                return "COMPLETED_ON_TIME"

            return "COMPLETED_LATE"

        if timezone.now() > obj.resolution_deadline:
            return "BREACHED"

        return "ON_TRACK"

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user if request else None

        # Superusers bypass organization validation.
        if not user or user.is_superuser:
            return attrs

        # Prevent changing an existing ticket's organization.
        if self.instance and "organization" in attrs:
            if attrs["organization"].id != self.instance.organization_id:
                raise serializers.ValidationError({
                    "organization": (
                        "You cannot change a ticket's organization."
                    )
                })

        # Determine the ticket organization.
        organization = attrs.get(
            "organization",
            self.instance.organization if self.instance else None,
        )

        if not user.organization_id:
            raise PermissionDenied(
                "You must belong to an organization to create a ticket."
            )

        if organization and organization.id != user.organization_id:
            raise PermissionDenied(
                "You can only use your own organization."
            )

        # Only ADMIN and MANAGER can change assignments.
        if "assigned_to" in attrs:
            assigned_to = attrs["assigned_to"]

            if user.role not in ["ADMIN", "MANAGER"]:
                current_assignee = (
                    self.instance.assigned_to
                    if self.instance
                    else None
                )

                if assigned_to != current_assignee:
                    raise serializers.ValidationError({
                        "assigned_to": (
                            "You cannot change ticket assignments."
                        )
                    })

            # Assignee must belong to the same organization.
            if assigned_to and (
                not organization
                or assigned_to.organization_id != organization.id
            ):
                raise serializers.ValidationError({
                    "assigned_to": (
                        "The assignee must belong to the ticket's organization."
                    )
                })

        return attrs
