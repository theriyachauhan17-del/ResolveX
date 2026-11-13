
from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User
from organizations.models import Organization
from .models import SLAPolicy


class SLAPolicySecurityTest(APITestCase):

    def setUp(self):
        self.organization_a = Organization.objects.create(
            name="Organization A",
            slug="organization-a",
        )

        self.organization_b = Organization.objects.create(
            name="Organization B",
            slug="organization-b",
        )

        self.manager = User.objects.create_user(
            username="sla_manager",
            password="TestPass123!",
            role=User.Role.MANAGER,
            organization=self.organization_a,
        )

        self.policy = SLAPolicy.objects.create(
            organization=self.organization_a,
            priority="HIGH",
            response_time_minutes=60,
            resolution_time_minutes=1440,
        )

        self.client.force_authenticate(user=self.manager)

    def test_manager_cannot_move_policy_to_another_organization(self):
        response = self.client.patch(
            f"/api/sla/policies/{self.policy.id}/",
            {"organization": self.organization_b.id},
            format="json",
        )

        self.policy.refresh_from_db()

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.policy.organization_id,
            self.organization_a.id,
        )
    
    def test_manager_can_update_policy_within_own_organization(self):
        response = self.client.patch(
            f"/api/sla/policies/{self.policy.id}/",
            {"response_time_minutes": 90},
            format="json",
        )

        self.policy.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.policy.response_time_minutes, 90)
        self.assertEqual(
            self.policy.organization_id,
            self.organization_a.id,
        )
    def test_agent_cannot_create_sla_policy(self):
        agent = User.objects.create_user(
            username="sla_agent",
            password="TestPass123!",
            role=User.Role.AGENT,
            organization=self.organization_a,
        )

        self.client.force_authenticate(user=agent)

        response = self.client.post(
            "/api/sla/policies/",
            {
                "organization": self.organization_a.id,
                "priority": "LOW",
                "response_time_minutes": 480,
                "resolution_time_minutes": 4320,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_agent_cannot_update_sla_policy(self):
        agent = User.objects.create_user(
            username="sla_agent_update",
            password="TestPass123!",
            role=User.Role.AGENT,
            organization=self.organization_a,
        )
        self.client.force_authenticate(user=agent)

        response = self.client.patch(
            f"/api/sla/policies/{self.policy.id}/",
            {"response_time_minutes": 120},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_create_sla_policy(self):
        customer = User.objects.create_user(
            username="sla_customer_create",
            password="TestPass123!",
            role=User.Role.CUSTOMER,
            organization=self.organization_a,
        )
        self.client.force_authenticate(user=customer)

        response = self.client.post(
            "/api/sla/policies/",
            {
                "organization": self.organization_a.id,
                "priority": "LOW",
                "response_time_minutes": 480,
                "resolution_time_minutes": 4320,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_update_sla_policy(self):
        customer = User.objects.create_user(
            username="sla_customer_update",
            password="TestPass123!",
            role=User.Role.CUSTOMER,
            organization=self.organization_a,
        )
        self.client.force_authenticate(user=customer)

        response = self.client.patch(
            f"/api/sla/policies/{self.policy.id}/",
            {"response_time_minutes": 120},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_view_another_organization_policy(self):
        other_policy = SLAPolicy.objects.create(
            organization=self.organization_b,
            priority="LOW",
            response_time_minutes=480,
            resolution_time_minutes=4320,
        )

        response = self.client.get(
            f"/api/sla/policies/{other_policy.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_without_organization_cannot_view_policies(self):
        user = User.objects.create_user(
            username="sla_no_org",
            password="TestPass123!",
            role=User.Role.AGENT,
        )
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/sla/policies/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_user_cannot_create_policy_for_another_organization(self):
        response = self.client.post(
            "/api/sla/policies/",
            {
                "organization": self.organization_b.id,
                "priority": "LOW",
                "response_time_minutes": 480,
                "resolution_time_minutes": 4320,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_create_policy_for_own_organization(self):
        response = self.client.post(
            "/api/sla/policies/",
            {
                "organization": self.organization_a.id,
                "priority": "LOW",
                "response_time_minutes": 480,
                "resolution_time_minutes": 4320,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_user_cannot_access_policies(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/sla/policies/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_superuser_can_access_policies_across_organizations(self):
        superuser = User.objects.create_superuser(
            username="sla_superuser",
            email="sla_superuser@example.com",
            password="TestPass123!",
        )
        SLAPolicy.objects.create(
            organization=self.organization_b,
            priority="LOW",
            response_time_minutes=480,
            resolution_time_minutes=4320,
        )

        self.client.force_authenticate(user=superuser)

        response = self.client.get("/api/sla/policies/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)