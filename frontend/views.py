
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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

    return render(
        request,
        "frontend/tickets.html",
        {"tickets": tickets},
    )


@login_required
def create_ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)

        if form.is_valid():
            ticket = form.save(commit=False)

            # Assign organization and creator from the logged-in user.
            if not request.user.organization_id:
                form.add_error(
                    None,
                    "Your account is not assigned to an organization.",
                )
            else:
                ticket.organization = request.user.organization
                ticket.created_by = request.user
                ticket.save()
                return redirect("tickets_page")
    else:
        form = TicketForm()

    return render(
        request,
        "frontend/create_ticket.html",
        {"form": form},
    )


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
