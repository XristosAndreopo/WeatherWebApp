from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class PasswordChangeTests(TestCase):
    def setUp(self):
        self.username = 'pwuser'
        self.old_password = 'OldPass123'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.old_password
        )
        self.client = Client()
        self.client.login(username=self.username, password=self.old_password)

    def test_profile_page_has_change_password_link(self):
        resp = self.client.get(reverse('profile'))
        self.assertEqual(resp.status_code, 200)
        expected = f'href="{reverse("password_change")}"'
        self.assertContains(resp, expected,
            msg_prefix="Profile page must link to password_change"
        )

    def test_password_change_get_renders_form(self):
        url = reverse('password_change')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        for field in ['old_password', 'new_password1', 'new_password2']:
            self.assertContains(resp, f'name="{field}"')

    def test_password_change_valid_post_updates_password(self):
        url = reverse('password_change')
        new_pass = 'NewStrongPass456'
        data = {
            'old_password': self.old_password,
            'new_password1': new_pass,
            'new_password2': new_pass,
        }
        resp = self.client.post(url, data, follow=True)
        self.assertRedirects(resp, reverse('password_change_done'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_pass))

    def test_password_change_invalid_post_shows_errors(self):
        url = reverse('password_change')
        data = {
            'old_password': self.old_password,
            'new_password1': 'abc',
            'new_password2': 'def',
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "The two password fields didn’t match")
