from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("tickets/", views.tickets_page, name="tickets_page"),
    path("tickets/create/", views.create_ticket, name="create_ticket"),
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_page, name="logout"),
    path("tickets/<int:ticket_id>/", views.ticket_detail, name="ticket_detail"),
    path("tickets/<int:ticket_id>/status/", views.update_ticket_status, name="update_ticket_status"),
    path("temporary-manager-reset/",views.temporary_manager_password_reset, name="temporary_manager_password_reset"),
    path("temporary-manager-reset/", views.temporary_manager_password_reset, name="temporary_manager_password_reset"),

]
