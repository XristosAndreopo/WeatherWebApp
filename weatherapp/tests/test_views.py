from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from weather.utils import ForecastCard

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

    @patch('weather.views.WeatherService.by_coords')
    def test_map_weather_data_json(self, mock_by_coords):
        mock_by_coords.return_value = ([], 'StubCity', 'SC', 0.0, 0.0)
        self.client.login(username='testuser', password='pass')
        resp = self.client.get(reverse('map_weather_data'), {'lat': 0, 'lng': 0})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['forecast'], [])
        self.assertEqual(data['location'], 'StubCity')
        self.assertIn('unit', data)

    @patch('weather.views.WeatherService.hourly_by_coords')
    def test_map_hourly_data_json(self, mock_hourly_by_coords):
        mock_hourly_by_coords.return_value = [{'dt': 1, 'temp': 2}]
        self.client.login(username='testuser', password='pass')
        resp = self.client.get(reverse('map_hourly_data'), {'lat': 0, 'lng': 0})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['hourly'], [{'dt': 1, 'temp': 2}])
        self.assertIn('unit', data)

    @patch('weather.views.WeatherService.by_city')
    def test_add_and_remove_favorite(self, mock_by_city):
        # Stub out by_city so favorites view won't hit the real API
        dummy = ForecastCard(
            date='2025-07-06 12:00',
            description='clear sky',
            temp=25,
            humidity=50,
            icon='clear.png'
        )
        mock_by_city.return_value = ([dummy, dummy], 'TestCity', 'TC', 0.0, 0.0)

        self.client.login(username='testuser', password='pass')

        # Add
        resp = self.client.post(
            reverse('add_favorite'),
            {'city': 'TestCity', 'country': 'TC'},
            follow=True
        )
        self.assertContains(resp, 'added to favorites', status_code=200)

        # List
        resp = self.client.get(reverse('favorites'))
        self.assertContains(resp, 'TestCity')

        # Remove
        fav_id = resp.context['favorite_weather'][0]['id']
        resp = self.client.post(
            reverse('remove_favorite', args=[fav_id]),
            follow=True
        )
        self.assertContains(resp, 'Favorite removed', status_code=200)
