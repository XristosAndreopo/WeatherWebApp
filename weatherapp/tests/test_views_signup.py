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
            'email': 'new@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        # Do not follow redirects here
        resp = self.client.post(self.url, data)
        # Should return a 302 redirect to home
        self.assertRedirects(resp, reverse('home'))
        # User created with the right email, and logged in
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertIn('_auth_user_id', self.client.session)


    def test_signup_post_password_mismatch(self):
        data = {
            'username':  'user2',
            'password1': 'Password123',
            'password2': 'Different123'
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(
            resp,
            "The two password fields didn’t match",
            msg_prefix="Expected mismatch error on the signup form"
        )
        self.assertFalse(User.objects.filter(username='user2').exists())
