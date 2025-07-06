# tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')

    def test_home_page_accessible(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_about_contact_profile(self):
        # About and Contact should be public
        for name in ('about', 'contact'):
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 200)

        # Profile requires login
        resp = self.client.get(reverse('profile'))
        self.assertRedirects(
            resp, f"{reverse('login')}?next={reverse('profile')}"
        )

    def test_find_and_map_require_login(self):
        for name in ('find_location', 'map', 'favorites', 'settings'):
            url = reverse(name)
            resp = self.client.get(url)
            self.assertRedirects(resp, f"{reverse('login')}?next={url}")

    def test_map_weather_data_json(self):
        self.client.login(username='testuser', password='pass')
        resp = self.client.get(reverse('map_weather_data'), {'lat': 0, 'lng': 0})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('forecast', data)
        self.assertIn('location', data)
        self.assertIn('unit', data)

    def test_map_hourly_data_json(self):
        self.client.login(username='testuser', password='pass')
        resp = self.client.get(reverse('map_hourly_data'), {'lat': 0, 'lng': 0})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('hourly', data)
        self.assertIn('unit', data)

    def test_add_and_remove_favorite(self):
        self.client.login(username='testuser', password='pass')
        # Add
        resp = self.client.post(reverse('add_favorite'), {'city': 'TestCity', 'country': 'TC'}, follow=True)
        self.assertContains(resp, 'added to favorites', status_code=200)
        # List
        resp = self.client.get(reverse('favorites'))
        self.assertContains(resp, 'TestCity')
        # Remove
        fav_id = resp.context['favorite_weather'][0]['id']
        resp = self.client.post(reverse('remove_favorite', args=[fav_id]), follow=True)
        self.assertContains(resp, 'Favorite removed', status_code=200)
