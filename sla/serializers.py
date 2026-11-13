from rest_framework import serializers
from .models import SLAPolicy


class SLAPolicySerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    class Meta:
        model = SLAPolicy
        fields = [
            "id",
            "organization",
            "organization_name",
            "priority",
            "response_time_minutes",
            "resolution_time_minutes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]