# File: tests/test_views_signup.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class SignUpViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('signup')

    def test_signup_get_renders_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'weather/signup.html')
        self.assertContains(resp, '<form')

    def test_signup_post_success(self):
        data = {
            'username':  'newuser',
            'email':     'new@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        resp = self.client.post(self.url, data, follow=True)
        # Should create user and redirect to home
        self.assertRedirects(resp, reverse('home'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # Ensure user is logged in
        session_key = self.client.session.get('_auth_user_id')
        self.assertEqual(int(session_key), User.objects.get(username='newuser').id)
        # Should see success message
        self.assertContains(resp, "Account created successfully")

    def test_signup_post_password_mismatch(self):
        data = {
            'username':  'user2',
            'email':     'u2@example.com',
            'password1': 'Password123',
            'password2': 'Different123'
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 200)
        # Form should show the password mismatch error
        self.assertFormError(
            resp, 'form', 'password2',
            "The two password fields didn’t match."
        )
        self.assertFalse(User.objects.filter(username='user2').exists())
