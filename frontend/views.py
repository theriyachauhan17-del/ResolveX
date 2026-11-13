
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from sla.models import SLAPolicy
from tickets.models import Ticket
from .forms import TicketForm


def home(request):
    return render(request, "frontend/home.html")


@login_required
def tickets_page(request):
    if not request.user.organization_id:
        return render(
            request,
            "frontend/tickets.html",
            {
                "tickets": Ticket.objects.none(),
                "organization_error": (
                    "Your account is not assigned to an organization."
                ),
            },
        )

    tickets = Ticket.objects.filter(
        organization_id=request.user.organization_id
    ).select_related(
        "organization",
        "created_by",
        "assigned_to",
    )

    search_query = request.GET.get("q", "").strip()
    if search_query:
        tickets = tickets.filter(title__icontains=search_query)

    selected_status = request.GET.get("status", "").strip()
    if selected_status:
        tickets = tickets.filter(status=selected_status)

    selected_priority = request.GET.get("priority", "").strip()
    if selected_priority:
        tickets = tickets.filter(priority=selected_priority)

    context = {
        "tickets": tickets,
        "search_query": search_query,
        "selected_status": selected_status,
        "selected_priority": selected_priority,
        "status_choices": Ticket.Status.choices,
        "priority_choices": Ticket.Priority.choices,
    }

    return render(request, "frontend/tickets.html", context)


@login_required
def ticket_detail(request, ticket_id):
    if not request.user.organization_id and not request.user.is_superuser:
        return render(
            request,
            "frontend/tickets.html",
            {
                "tickets": Ticket.objects.none(),
                "organization_error": (
                    "Your account is not assigned to an organization."
                ),
            },
            status=403,
        )

    ticket_queryset = Ticket.objects.select_related(
        "organization",
        "created_by",
        "assigned_to",
    )

    if not request.user.is_superuser:
        ticket_queryset = ticket_queryset.filter(
            organization_id=request.user.organization_id
        )

    ticket = get_object_or_404(ticket_queryset, pk=ticket_id)

    return render(
        request,
        "frontend/ticket_detail.html",
        {
            "ticket": ticket,
            "status_choices": Ticket.Status.choices,
        },
    )


@login_required
def create_ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)

        if form.is_valid():
            if not request.user.organization_id:
                form.add_error(
                    None,
                    "Your account is not assigned to an organization.",
                )
            else:
                ticket = form.save(commit=False)
                organization = request.user.organization

                sla_policy = SLAPolicy.objects.filter(
                    organization=organization,
                    priority=ticket.priority,
                    is_active=True,
                ).first()

                ticket.organization = organization
                ticket.created_by = request.user

                if sla_policy:
                    now = timezone.now()

                    ticket.response_deadline = now + timedelta(
                        minutes=sla_policy.response_time_minutes
                    )

                    ticket.resolution_deadline = now + timedelta(
                        minutes=sla_policy.resolution_time_minutes
                    )

                ticket.save()

                messages.success(
                    request,
                    "Ticket created successfully.",
                )
                return redirect("tickets_page")
    else:
        form = TicketForm()

    return render(
        request,
        "frontend/create_ticket.html",
        {"form": form},
    )


@login_required
def update_ticket_status(request, ticket_id):
    if request.method != "POST":
        return redirect("ticket_detail", ticket_id=ticket_id)

    user = request.user

    ticket_queryset = Ticket.objects.all()

    if not user.is_superuser:
        if not user.organization_id:
            return render(
                request,
                "frontend/tickets.html",
                {
                    "tickets": Ticket.objects.none(),
                    "organization_error": (
                        "Your account is not assigned to an organization."
                    ),
                },
                status=403,
            )

        ticket_queryset = ticket_queryset.filter(
            organization_id=user.organization_id
        )

    ticket = get_object_or_404(ticket_queryset, pk=ticket_id)

    allowed = (
        user.is_superuser
        or user.role in ["ADMIN", "MANAGER"]
        or (
            user.role == "AGENT"
            and ticket.assigned_to_id == user.id
        )
    )

    if not allowed:
        return render(
            request,
            "frontend/ticket_detail.html",
            {
                "ticket": ticket,
                "status_error": (
                    "You do not have permission to update this ticket."
                ),
            },
            status=403,
        )

    new_status = request.POST.get("status", "").strip()
    valid_statuses = dict(Ticket.Status.choices)

    if new_status not in valid_statuses:
        messages.error(request, "Please select a valid ticket status.")
        return redirect("ticket_detail", ticket_id=ticket.id)

    old_status = ticket.status
    now = timezone.now()
    update_fields = []

    if (
        old_status != Ticket.Status.IN_PROGRESS
        and new_status == Ticket.Status.IN_PROGRESS
        and ticket.first_responded_at is None
    ):
        ticket.first_responded_at = now
        update_fields.append("first_responded_at")

    if (
        old_status != Ticket.Status.RESOLVED
        and new_status == Ticket.Status.RESOLVED
    ):
        ticket.resolved_at = now
        update_fields.append("resolved_at")

    if old_status != new_status:
        ticket.status = new_status
        update_fields.extend(["status", "updated_at"])

    if update_fields:
        ticket.save(update_fields=update_fields)

    messages.success(request, "Ticket status updated successfully.")
    return redirect("ticket_detail", ticket_id=ticket.id)


def login_page(request):
    if request.user.is_authenticated:
        return redirect("tickets_page")

    error_message = None

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("tickets_page")

        error_message = "Invalid username or password."

    return render(
        request,
        "frontend/login.html",
        {"error_message": error_message},
    )


def logout_page(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")

    return redirect("home")
