
from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "organization",
        "priority",
        "status",
        "created_by",
        "assigned_to",
        "created_at",
    )

    list_filter = ("priority", "status", "organization")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("organization", "created_by", "assigned_to")
    ordering = ("-created_at",)
