
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from .models import SLAPolicy
from .serializers import SLAPolicySerializer
from .permissions import SLAPolicyPermission


class SLAPolicyViewSet(viewsets.ModelViewSet):
    serializer_class = SLAPolicySerializer
    permission_classes = [SLAPolicyPermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return SLAPolicy.objects.select_related(
                "organization"
            ).all()

        if user.organization_id:
            return SLAPolicy.objects.select_related(
                "organization"
            ).filter(organization_id=user.organization_id)

        return SLAPolicy.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        organization = serializer.validated_data["organization"]

        if not user.is_superuser:
            if not user.organization_id:
                raise PermissionDenied(
                    "You must belong to an organization to create an SLA policy."
                )

            if organization.id != user.organization_id:
                raise PermissionDenied(
                    "You can create SLA policies only for your own organization."
                )

        serializer.save()
