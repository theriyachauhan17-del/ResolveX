
from django.db import models
from organizations.models import Organization


class SLAPolicy(models.Model):

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="sla_policies",
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
    )

    response_time_minutes = models.PositiveIntegerField()
    resolution_time_minutes = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["organization", "priority"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "priority"],
                name="unique_sla_policy_per_org_priority",
            )
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.priority} SLA"
