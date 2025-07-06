# tests/test_services.py

import time
from django.test import TestCase
from unittest.mock import patch

from weather.services import WeatherService, WeatherAPIError
from weather.utils import ForecastCard

class WeatherServiceTests(TestCase):
    @patch('weather.services.WeatherService._call')
    @patch('weather.services.parse_daily_forecasts')
    def test_by_city_success(self, mock_parse, mock_call):
        # Prepare fake API response
        fake_data = {
            'city': {'name': 'TestCity', 'country': 'TC', 'coord': {'lat': 1.23, 'lon': 4.56}},
            'list': [{'dummy': 'data'}]
        }
        mock_call.return_value = fake_data

        # Prepare fake parse result
        fake_card = ForecastCard(
            date='2025-01-01 00:00',
            description='clear sky',
            temp=10,
            humidity=50,
            icon='clear.png'
        )
        mock_parse.return_value = [fake_card]

        cards, city, country, lat, lon = WeatherService.by_city(
            'City', 'CT', days=1, units='metric'
        )
        self.assertEqual(cards, [fake_card])
        self.assertEqual(city, 'TestCity')
        self.assertEqual(country, 'TC')
        self.assertEqual(lat, 1.23)
        self.assertEqual(lon, 4.56)

    @patch('weather.services.WeatherService._call')
    def test_by_city_raises_api_error(self, mock_call):
        mock_call.side_effect = WeatherAPIError("API failure")
        with self.assertRaises(WeatherAPIError):
            WeatherService.by_city('City', None)

    @patch('weather.services.WeatherService._call')
    def test_hourly_by_coords(self, mock_call):
        # Create fake hourly data
        now = int(time.time())
        fake_list = [
            {'dt': now, 'main': {'temp': 12}},
            {'dt': now + 3600, 'main': {'temp': 15}},
        ]
        mock_call.return_value = {'list': fake_list}

        result = WeatherService.hourly_by_coords(
            lat=1.0, lon=2.0, hours=2, step=1, units='metric'
        )
        # Verify structure
        self.assertIsInstance(result, list)
        self.assertTrue(all('dt' in entry and 'temp' in entry for entry in result))
        self.assertEqual(len(result), 2)
