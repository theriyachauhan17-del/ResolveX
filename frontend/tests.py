
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from organizations.models import Organization
from tickets.models import Ticket


User = get_user_model()


class TicketStatusUpdateViewTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-organization",
        )

        self.manager = User.objects.create_user(
            username="testmanager",
            password="TestPass123!",
            role="MANAGER",
            organization=self.organization,
        )

        self.ticket = Ticket.objects.create(
            organization=self.organization,
            title="Login issue",
            description="Unable to log in.",
            priority=Ticket.Priority.HIGH,
            status=Ticket.Status.OPEN,
            created_by=self.manager,
        )

        self.update_url = reverse(
            "update_ticket_status",
            args=[self.ticket.id],
        )

    def test_manager_can_update_status(self):
        self.client.force_login(self.manager)

        response = self.client.post(
            self.update_url,
            {"status": Ticket.Status.IN_PROGRESS},
        )

        self.assertRedirects(
            response,
            reverse("ticket_detail", args=[self.ticket.id]),
        )

        self.ticket.refresh_from_db()
        self.assertEqual(
            self.ticket.status,
            Ticket.Status.IN_PROGRESS,
        )

    def test_customer_cannot_update_status(self):
        customer = User.objects.create_user(
            username="testcustomer",
            password="TestPass123!",
            role="CUSTOMER",
            organization=self.organization,
        )

        self.client.force_login(customer)

        response = self.client.post(
            self.update_url,
            {"status": Ticket.Status.RESOLVED},
        )

        self.assertEqual(response.status_code, 403)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)

    def test_manager_cannot_update_other_organization_ticket(self):
        other_organization = Organization.objects.create(
            name="Other Organization",
            slug="other-organization",
        )

        other_ticket = Ticket.objects.create(
            organization=other_organization,
            title="Private ticket",
            description="Another organization's ticket.",
            created_by=self.manager,
        )

        self.client.force_login(self.manager)

        response = self.client.post(
            reverse(
                "update_ticket_status",
                args=[other_ticket.id],
            ),
            {"status": Ticket.Status.RESOLVED},
        )

        self.assertEqual(response.status_code, 404)

        other_ticket.refresh_from_db()
        self.assertEqual(other_ticket.status, Ticket.Status.OPEN)

    def test_invalid_status_does_not_change_ticket(self):
        self.client.force_login(self.manager)

        response = self.client.post(
            self.update_url,
            {"status": "INVALID_STATUS"},
        )

        self.assertRedirects(
            response,
            reverse("ticket_detail", args=[self.ticket.id]),
        )

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)

    def test_unauthenticated_user_cannot_update_status(self):
        response = self.client.post(
            self.update_url,
            {"status": Ticket.Status.RESOLVED},
        )

        self.assertEqual(response.status_code, 302)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)

    
    def test_assigned_agent_can_update_ticket(self):
        agent = User.objects.create_user(
            username="assignedagent",
            password="TestPass123!",
            role="AGENT",
            organization=self.organization,
        )
        self.ticket.assigned_to = agent
        self.ticket.save()

        self.client.force_login(agent)
        response = self.client.post(
            self.update_url,
            {"status": Ticket.Status.IN_PROGRESS},
        )

        self.assertRedirects(
            response,
            reverse("ticket_detail", args=[self.ticket.id]),
        )
        self.ticket.refresh_from_db()
        self.assertEqual(
            self.ticket.status,
            Ticket.Status.IN_PROGRESS,
        )

    def test_agent_cannot_update_ticket_assigned_to_another_agent(self):
        agent = User.objects.create_user(
            username="unassignedagent",
            password="TestPass123!",
            role="AGENT",
            organization=self.organization,
        )
        other_agent = User.objects.create_user(
            username="otheragent",
            password="TestPass123!",
            role="AGENT",
            organization=self.organization,
        )
        self.ticket.assigned_to = other_agent
        self.ticket.save()

        self.client.force_login(agent)
        response = self.client.post(
            self.update_url,
            {"status": Ticket.Status.RESOLVED},
        )

        self.assertEqual(response.status_code, 403)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)

    def test_user_without_organization_cannot_update_ticket(self):
        user = User.objects.create_user(
            username="noorganization",
            password="TestPass123!",
            role="MANAGER",
        )

        self.client.force_login(user)
        response = self.client.post(
            self.update_url,
            {"status": Ticket.Status.RESOLVED},
        )

        self.assertEqual(response.status_code, 403)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)

