from django.test import Client, TestCase
from django.urls import reverse

from users.models import User


class LogoutViewTests(TestCase):
    def test_logout_clears_authenticated_session(self):
        user = User.objects.create_user(
            email="user@example.com",
            password="password123",
        )
        self.client.force_login(user)

        response = self.client.post("/api-auth/logout/")

        self.assertEqual(response.status_code, 204)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_drf_browsable_api_logout_url_is_available(self):
        self.assertEqual(reverse("rest_framework:logout"), "/api-auth/browser/logout/")


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True, HTTP_HOST="localhost")
        User.objects.create_user(
            email="user@example.com",
            password="password123",
        )

    def test_login_requires_csrf_token(self):
        response = self.client.post(
            "/api-auth/login/",
            {"username": "user@example.com", "password": "password123"},
        )

        self.assertEqual(response.status_code, 403)

    def test_login_succeeds_with_csrf_cookie_and_header(self):
        csrf_response = self.client.get("/api-auth/csrf/")
        csrf_token = csrf_response.json()["csrfToken"]

        response = self.client.post(
            "/api-auth/login/",
            {"username": "user@example.com", "password": "password123"},
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "user@example.com")
