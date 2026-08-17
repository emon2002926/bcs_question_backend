from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="oldpassword123",
            is_active=True,
            is_verified=True
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        self.url = '/api/auth/change-password/'

    def test_change_password_success(self):
        data = {
            "current_password": "oldpassword123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_change_password_with_incorrect_current_password(self):
        data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get('success'))

    def test_change_password_mismatch_confirm_password(self):
        data = {
            "current_password": "oldpassword123",
            "new_password": "newpassword123",
            "confirm_password": "mismatchpassword"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_same_as_current(self):
        data = {
            "current_password": "oldpassword123",
            "new_password": "oldpassword123"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        self.client.credentials()  # remove credentials
        data = {
            "current_password": "oldpassword123",
            "new_password": "newpassword123"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

