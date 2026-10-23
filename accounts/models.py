
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        MANAGER = "MANAGER", "Manager"
        AGENT = "AGENT", "Support Agent"
        CUSTOMER = "CUSTOMER", "Customer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    def __str__(self):
        return self.username
