from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import CustomUser, Department, Role


class UserTest(APITestCase):
    def setUp(self):
        self.test_user = CustomUser.objects.create_user(
            "testuser", "test@example.com", "testpassword"
        )

    def test_create_user(self):
        """
        Ensure we can create a new user
        """
        user = CustomUser.objects.create(
            username="johndoe",
            first_name="John",
            middle_name="Doe",
            last_name="Donny",
        )

        user.set_password("somepassword")

        self.assertEqual(CustomUser.objects.count(), 2)
        self.assertEqual(user.username, "johndoe")

    def test_create_user_with_role(self):
        role = Role.objects.create(id=1)
        user = CustomUser.objects.create(
            username="toddtest",
            first_name="Todd",
            middle_name="Philips",
            last_name="Junior",
        )

        user.roles.add(role)

        self.assertEqual(user.roles.first(), role)

    def test_create_user_with_roles(self):
        role_one = Role.objects.create(id=2)
        role_two = Role.objects.create(id=3)
        user = CustomUser.objects.first()
        user.roles.add(role_one, role_two)

        self.assertEqual(user.roles.all().count(), 2)

    def test_create_user_with_department(self):
        department = Department.objects.create(name="Computer Science")
        user = CustomUser.objects.create(
            username="Tony", department=department
        )

        self.assertEqual(user.userprofile.department.name, department.name)

    def test_user_can_obtain_token(self):
        token_obtain_url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(token_obtain_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_can_refresh_token(self):
        token_obtain_url = reverse("token_obtain_pair")
        token_refresh_url = reverse("token_refresh")
        data = {"username": "testuser", "password": "testpassword"}
        token_obtain = self.client.post(token_obtain_url, data, format="json")
        refresh_token = {"refresh": token_obtain.data["refresh"]}
        response = self.client.post(
            token_refresh_url, refresh_token, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)