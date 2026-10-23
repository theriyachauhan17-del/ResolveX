
from rest_framework import serializers
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
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user if request else None

        # Keep existing behavior for superusers.
        if not user or user.is_superuser:
            return attrs

        # Prevent moving an existing ticket to another organization.
        if self.instance and "organization" in attrs:
            if attrs["organization"].id != self.instance.organization_id:
                raise serializers.ValidationError({
                    "organization": (
                        "You cannot change a ticket's organization."
                    )
                })

        # New and existing tickets must belong to the user's organization.
        organization = attrs.get(
            "organization",
            self.instance.organization if self.instance else None,
        )

        if not user.organization_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "You must belong to an organization to create a ticket."
            )

        if organization and organization.id != user.organization_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "You can only use your own organization."
            )

        # Only ADMIN and MANAGER can change ticket assignments.
        if "assigned_to" in attrs:
            assigned_to = attrs["assigned_to"]

            if user.role not in ["ADMIN", "MANAGER"]:
                current_assignee = (
                    self.instance.assigned_to if self.instance else None
                )
                if assigned_to != current_assignee:
                    raise serializers.ValidationError({
                        "assigned_to": (
                            "You cannot change ticket assignments."
                        )
                    })

            # The assignee must belong to the ticket's organization.
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
