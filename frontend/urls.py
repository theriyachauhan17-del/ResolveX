from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_page, name="logout"),
    path("tickets/", views.tickets_page, name="tickets_page"),
    path("tickets/create/", views.create_ticket, name="create_ticket"),
    path("tickets/<int:ticket_id>/", views.ticket_detail, name="ticket_detail"),
    path(
        "tickets/<int:ticket_id>/status/",
        views.update_ticket_status,
        name="update_ticket_status",
    ),
    path(
        "temporary-database-diagnostic/",
        views.temporary_database_diagnostic,
        name="temporary_database_diagnostic",
    ),
]
