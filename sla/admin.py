
from django.contrib import admin
from .models import SLAPolicy


@admin.register(SLAPolicy)
class SLAPolicyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization",
        "priority",
        "response_time_minutes",
        "resolution_time_minutes",
        "is_active",
    )

    list_filter = ("organization", "priority", "is_active")
    search_fields = ("organization__name",)
