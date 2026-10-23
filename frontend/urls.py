
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("tickets/", views.tickets_page, name="tickets_page"),
    path("tickets/create/", views.create_ticket, name="create_ticket"),
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_page, name="logout"),

]
