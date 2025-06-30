# weather/services.py

import requests
from django.conf import settings
from .constants import OPENWEATHER_BASE
from .utils import parse_daily_forecasts

class WeatherAPIError(Exception):
    """Raised when the OpenWeather API returns an error code."""

class WeatherService:
    @staticmethod
    def _call(params: dict) -> dict:
        params = params.copy()
        params['appid'] = settings.OPENWEATHER_API_KEY
        params['units'] = 'metric'
        resp = requests.get(OPENWEATHER_BASE, params=params, timeout=10)
        data = resp.json()
        if data.get('cod') not in (200, '200'):
            raise WeatherAPIError(data.get('message', 'API error'))
        return data

    @classmethod
    def by_city(cls, city: str, country: str | None = None, days: int = 7):
        query = f"{city},{country}" if country else city
        data = cls._call({'q': query})
        cards = parse_daily_forecasts(data['list'], days)
        return cards, data['city']['name'], data['city'].get('country', '')

    @classmethod
    def by_coords(cls, lat: float, lon: float, days: int = 7):
        data = cls._call({'lat': lat, 'lon': lon})
        cards = parse_daily_forecasts(data['list'], days)
        return cards, data['city']['name'], data['city'].get('country', '')
