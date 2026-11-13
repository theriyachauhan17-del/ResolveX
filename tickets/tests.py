from datetime import timedelta
from django.utils import timezone

from sla.models import SLAPolicy
from tickets.serializers import TicketSerializer
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from organizations.models import Organization
from tickets.models import Ticket


User = get_user_model()


class TicketAuthenticationTest(APITestCase):

    def test_ticket_list_requires_authentication(self):
        response = self.client.get("/api/tickets/")

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )


class TicketCreationTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testagent",
            password="TestPass123!"
        )

        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-organization"
        )

        self.user.organization = self.organization
        self.user.save()

        self.client.force_authenticate(user=self.user)


    def test_user_without_organization_cannot_create_ticket(self):
        self.user.organization = None
        self.user.save()

        data = {
            "organization": self.organization.id,
            "title": "Ticket without organization membership",
            "description": "This request should be rejected",
            "priority": "HIGH",
            "status": "OPEN",
        }

        response = self.client.post(
            "/api/tickets/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Ticket.objects.count(), 0)


    def test_authenticated_user_can_create_ticket(self):
        data = {
            "organization": self.organization.id,
            "title": "Login issue",
            "description": "Unable to log in to the application",
            "priority": "HIGH",
            "status": "OPEN",
        }

        response = self.client.post(
            "/api/tickets/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(Ticket.objects.count(), 1)

        ticket = Ticket.objects.get()
        self.assertEqual(ticket.title, "Login issue")
        self.assertEqual(ticket.created_by, self.user)

    def test_ticket_creation_requires_title(self):
        data = {
            "organization": self.organization.id,
            "description": "Ticket without a title",
            "priority": "HIGH",
            "status": "OPEN",
        }

        response = self.client.post(
            "/api/tickets/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertIn("title", response.data)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_regular_user_cannot_see_tickets_in_list(self):
        response = self.client.get("/api/tickets/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_superuser_can_access_ticket_list(self):
        admin_user = User.objects.create_superuser(
            username="testadmin",
            email="admin@example.com",
            password="AdminPass123!"
        )

        self.client.force_authenticate(user=admin_user)

        response = self.client.get("/api/tickets/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])


    def test_user_cannot_create_ticket_for_other_organization(self):
        other_organization = Organization.objects.create(
            name="Other Organization",
            slug="other-organization",
        )

        data = {
            "organization": other_organization.id,
            "title": "Unauthorized ticket",
            "description": "This should be rejected",
            "priority": "HIGH",
            "status": "OPEN",
        }

        response = self.client.post(
            "/api/tickets/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Ticket.objects.count(), 0)

    def test_user_can_see_tickets_from_own_organization(self):
        self.user.organization = self.organization
        self.user.save()

        Ticket.objects.create(
            organization=self.organization,
            title="My organization's ticket",
            description="Test ticket",
            created_by=self.user,
        )

        response = self.client.get("/api/tickets/")

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["title"],
            "My organization's ticket",
        )

    def test_user_cannot_see_other_organization_tickets(self):
        other_organization = Organization.objects.create(
            name="Other Organization",
            slug="other-organization",
        )

        self.user.organization = self.organization
        self.user.save()

        Ticket.objects.create(
            organization=other_organization,
            title="Other organization's ticket",
            description="Private test ticket",
            created_by=self.user,
        )

        response = self.client.get("/api/tickets/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_superuser_can_create_ticket_for_other_organization(self):
        admin_user = User.objects.create_superuser(
            username="admincreator",
            email="admincreator@example.com",
            password="AdminPass123!",
        )

        other_organization = Organization.objects.create(
            name="Another Organization",
            slug="another-organization",
        )

        self.client.force_authenticate(user=admin_user)

        data = {
            "organization": other_organization.id,
            "title": "Admin-created ticket",
            "description": "Created by a superuser",
            "priority": "HIGH",
            "status": "OPEN",
        }

        response = self.client.post(
            "/api/tickets/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Ticket.objects.count(), 1)

        ticket = Ticket.objects.get()
        self.assertEqual(ticket.organization, other_organization)
        self.assertEqual(ticket.created_by, admin_user)


    def test_manager_can_update_ticket_in_own_organization(self):
        self.user.role = User.Role.MANAGER
        self.user.save()

        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Manager update test",
            description="Testing manager permissions",
            created_by=self.user,
        )

        response = self.client.patch(
            f"/api/tickets/{ticket.id}/",
            {"status": "IN_PROGRESS"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, "IN_PROGRESS")


    def test_manager_cannot_update_ticket_in_another_organization(self):
        self.user.role = User.Role.MANAGER
        self.user.save()

        other_organization = Organization.objects.create(
            name="Separate Organization",
            slug="separate-organization",
        )

        ticket = Ticket.objects.create(
            organization=other_organization,
            title="Other organization ticket",
            description="This ticket must remain protected",
            created_by=self.user,
        )

        response = self.client.patch(
            f"/api/tickets/{ticket.id}/",
            {"status": "RESOLVED"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        ticket.refresh_from_db()
        self.assertNotEqual(ticket.status, "RESOLVED")



    def test_manager_cannot_delete_ticket(self):
        self.user.role = User.Role.MANAGER
        self.user.save()

        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Manager deletion test",
            description="A manager should not delete this ticket",
            created_by=self.user,
        )

        response = self.client.delete(
            f"/api/tickets/{ticket.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(
            Ticket.objects.filter(id=ticket.id).exists()
        )


    def test_agent_cannot_update_ticket_assigned_to_another_agent(self):
        self.user.role = User.Role.AGENT
        self.user.save()

        other_agent = User.objects.create_user(
            username="otheragent",
            password="TestPass123!",
            role=User.Role.AGENT,
            organization=self.organization,
        )

        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Assigned ticket",
            description="This ticket belongs to another agent",
            created_by=self.user,
            assigned_to=other_agent,
        )

        response = self.client.patch(
            f"/api/tickets/{ticket.id}/",
            {"status": "RESOLVED"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        ticket.refresh_from_db()
        self.assertNotEqual(ticket.status, "RESOLVED")


    def test_customer_cannot_update_another_users_ticket(self):
        # Set the current user as a customer.
        self.user.role = User.Role.CUSTOMER
        self.user.save()

        # Create another customer in the same organization.
        other_customer = User.objects.create_user(
            username="othercustomer",
            password="TestPass123!",
            role=User.Role.CUSTOMER,
            organization=self.organization,
        )

        # Create a ticket owned by the other customer.
        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Another customer's ticket",
            description="This ticket belongs to another customer",
            created_by=other_customer,
        )

        # Try to update the other customer's ticket.
        response = self.client.patch(
            f"/api/tickets/{ticket.id}/",
            {"status": "RESOLVED"},
            format="json",
        )

        # The request should be denied.
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        # Confirm that the ticket was not changed.
        ticket.refresh_from_db()
        self.assertNotEqual(ticket.status, "RESOLVED")


    def test_customer_cannot_update_own_ticket(self):
        self.user.role = User.Role.CUSTOMER
        self.user.save()

        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Customer own ticket",
            description="Customer should not update this ticket",
            created_by=self.user,
        )

        response = self.client.patch(
            f"/api/tickets/{ticket.id}/",
            {"status": "RESOLVED"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, "OPEN")


    def test_superuser_can_update_ticket_in_another_organization(self):
        admin_user = User.objects.create_superuser(
            username="adminupdater",
            email="adminupdater@example.com",
            password="AdminPass123!",
        )

        other_organization = Organization.objects.create(
            name="Admin Test Organization",
            slug="admin-test-organization",
        )

        ticket = Ticket.objects.create(
            organization=other_organization,
            title="Ticket for admin update",
            description="This ticket belongs to another organization",
            created_by=self.user,
        )

        self.client.force_authenticate(user=admin_user)

        response = self.client.patch(
            f"/api/tickets/{ticket.id}/",
            {"status": "RESOLVED"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, "RESOLVED")


    def test_superuser_can_delete_ticket_in_another_organization(self):
        admin_user = User.objects.create_superuser(
            username="admindelete",
            email="admindelete@example.com",
            password="AdminPass123!",
        )

        other_organization = Organization.objects.create(
            name="Delete Test Organization",
            slug="delete-test-organization",
        )

        ticket = Ticket.objects.create(
            organization=other_organization,
            title="Ticket for admin deletion",
            description="Testing administrator deletion",
            created_by=self.user,
        )

        self.client.force_authenticate(user=admin_user)

        response = self.client.delete(
            f"/api/tickets/{ticket.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Ticket.objects.filter(id=ticket.id).exists()
        )


    def test_agent_can_update_ticket_assigned_to_them(self):
        self.user.role = User.Role.AGENT
        self.user.save()

        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Agent update test",
            description="Testing assigned agent permissions",
            created_by=self.user,
            assigned_to=self.user,
        )

        response = self.client.patch(
            f"/api/tickets/{ticket.id}/",
            {"status": "IN_PROGRESS"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, "IN_PROGRESS")


    def test_manager_cannot_move_ticket_to_another_organization(self):
        self.user.role = User.Role.MANAGER
        self.user.save()

        other_organization = Organization.objects.create(
            name="Target Organization",
            slug="target-organization",
        )

        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Protected ticket",
            description="Organization must not change",
            created_by=self.user,
        )

        response = self.client.patch(
            f"/api/tickets/{ticket.id}/",
            {"organization": other_organization.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        ticket.refresh_from_db()
        self.assertEqual(
            ticket.organization_id,
            self.organization.id,
        )

    def test_manager_cannot_assign_ticket_to_another_organization_user(self):
        self.user.role = User.Role.MANAGER
        self.user.save()

        other_organization = Organization.objects.create(
            name="Assignment Target Organization",
            slug="assignment-target-organization",
        )

        other_agent = User.objects.create_user(
            username="externalagent",
            password="TestPass123!",
            role=User.Role.AGENT,
            organization=other_organization,
        )

        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Assignment security test",
            description="Assignee must belong to the same organization",
            created_by=self.user,
        )

        response = self.client.patch(
            f"/api/tickets/{ticket.id}/",
            {"assigned_to": other_agent.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        ticket.refresh_from_db()
        self.assertIsNone(ticket.assigned_to_id)



class TicketSLATest(APITestCase):

    def setUp(self):
        self.organization = Organization.objects.create(
            name="SLA Test Organization",
            slug="sla-test-organization",
        )

        self.user = User.objects.create_user(
            username="slaagent",
            password="TestPass123!",
            organization=self.organization,
            role=User.Role.AGENT,
        )

        self.client.force_authenticate(user=self.user)

    def create_policy(self, priority, response_minutes, resolution_minutes):
        return SLAPolicy.objects.create(
            organization=self.organization,
            priority=priority,
            response_time_minutes=response_minutes,
            resolution_time_minutes=resolution_minutes,
            is_active=True,
        )

    def test_low_priority_ticket_gets_correct_sla_deadlines(self):
        self.create_policy("LOW", 480, 4320)

        before_creation = timezone.now()

        response = self.client.post(
            "/api/tickets/",
            {
                "organization": self.organization.id,
                "title": "Low priority SLA test",
                "description": "Testing LOW priority deadlines",
                "priority": "LOW",
                "status": "OPEN",
            },
            format="json",
        )

        after_creation = timezone.now()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ticket = Ticket.objects.get(title="Low priority SLA test")

        expected_response = timedelta(minutes=480)
        expected_resolution = timedelta(minutes=4320)

        self.assertGreaterEqual(
            ticket.response_deadline,
            before_creation + expected_response,
        )
        self.assertLessEqual(
            ticket.response_deadline,
            after_creation + expected_response,
        )

        self.assertGreaterEqual(
            ticket.resolution_deadline,
            before_creation + expected_resolution,
        )
        self.assertLessEqual(
            ticket.resolution_deadline,
            after_creation + expected_resolution,
        )

    def test_ticket_without_active_policy_has_no_deadlines(self):
        response = self.client.post(
            "/api/tickets/",
            {
                "organization": self.organization.id,
                "title": "No SLA policy test",
                "description": "Testing missing SLA policy",
                "priority": "LOW",
                "status": "OPEN",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ticket = Ticket.objects.get(title="No SLA policy test")

        self.assertIsNone(ticket.response_deadline)
        self.assertIsNone(ticket.resolution_deadline)

    def test_response_sla_completed_on_time(self):
        deadline = timezone.now() + timedelta(hours=1)

        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Response on time",
            description="Testing response SLA",
            created_by=self.user,
            response_deadline=deadline,
            first_responded_at=timezone.now(),
        )

        serializer = TicketSerializer(ticket)

        self.assertEqual(
            serializer.data["response_sla_status"],
            "COMPLETED_ON_TIME",
        )

    def test_response_sla_breached(self):
        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Response breached",
            description="Testing breached response SLA",
            created_by=self.user,
            response_deadline=timezone.now() - timedelta(minutes=5),
        )

        serializer = TicketSerializer(ticket)

        self.assertEqual(
            serializer.data["response_sla_status"],
            "BREACHED",
        )

    def test_resolution_sla_completed_on_time(self):
        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Resolution on time",
            description="Testing resolution SLA",
            created_by=self.user,
            status=Ticket.Status.RESOLVED,
            resolution_deadline=timezone.now() + timedelta(hours=1),
            resolved_at=timezone.now(),
        )

        serializer = TicketSerializer(ticket)

        self.assertEqual(
            serializer.data["resolution_sla_status"],
            "COMPLETED_ON_TIME",
        )

    def test_resolution_sla_completed_late(self):
        deadline = timezone.now() - timedelta(hours=1)

        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Resolution late",
            description="Testing late resolution",
            created_by=self.user,
            status=Ticket.Status.RESOLVED,
            resolution_deadline=deadline,
            resolved_at=timezone.now(),
        )

        serializer = TicketSerializer(ticket)

        self.assertEqual(
            serializer.data["resolution_sla_status"],
            "COMPLETED_LATE",
        )

    def test_reopened_ticket_continues_resolution_tracking(self):
        ticket = Ticket.objects.create(
            organization=self.organization,
            title="Reopened ticket",
            description="Testing reopened ticket SLA",
            created_by=self.user,
            status=Ticket.Status.IN_PROGRESS,
            resolution_deadline=timezone.now() + timedelta(hours=2),
            resolved_at=timezone.now() - timedelta(minutes=10),
        )

        serializer = TicketSerializer(ticket)

        self.assertEqual(
            serializer.data["resolution_sla_status"],
            "ON_TRACK",
        )

    def test_ticket_without_deadline_returns_not_configured(self):
        ticket = Ticket.objects.create(
            organization=self.organization,
            title="No deadline",
            description="Testing missing deadlines",
            created_by=self.user,
        )

        serializer = TicketSerializer(ticket)

        self.assertEqual(
            serializer.data["response_sla_status"],
            "NOT_CONFIGURED",
        )

        self.assertEqual(
            serializer.data["resolution_sla_status"],
            "NOT_CONFIGURED",
        )
