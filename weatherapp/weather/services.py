# File: weather/services.py

"""
weather/services.py

Abstraction layer for calling the OpenWeatherMap API and transforming data into
templates-friendly structures.

Features:
  - by_city(city, country, …) → forecast data + location
  - by_coords(lat, lon, …)
  - hourly_by_coords(lat, lon) → simplified hourly forecast
"""

import requests
from django.conf import settings

from .constants import OPENWEATHER_BASE
from .utils import parse_daily_forecasts


class WeatherAPIError(Exception):
    """Custom exception for handling OpenWeatherMap-related API failures."""


class WeatherService:
    """
    API client wrapper for OpenWeatherMap 5-day forecast endpoint.

    Provides:
      - by_city(): search by city name (and optional country)
      - by_coords(): search using lat/lon
      - hourly_by_coords(): next 24h hourly temperatures
    """

    @staticmethod
    def _call(params: dict, units: str) -> dict:
        """
        Internal method to call OpenWeather API with given parameters.
        Raises WeatherAPIError on bad response.
        """
        payload = {
            **params,
            'appid': settings.OPENWEATHER_API_KEY,
            'units': units
        }

        response = requests.get(OPENWEATHER_BASE, params=payload, timeout=10)
        data = response.json()

        if data.get('cod') not in (200, '200'):
            raise WeatherAPIError(data.get('message', 'Unknown API error'))

        return data

    @classmethod
    def by_city(cls, city: str, country: str | None = None, days: int = 7, units: str = 'metric') -> tuple[list, str, str, float, float]:
        """
        Query forecast using city name and optional country code.

        Returns:
          (cards, city_name, country_code, lat, lon)
        """
        q = f"{city},{country}" if country else city
        data = cls._call({'q': q}, units=units)
        cards = parse_daily_forecasts(data['list'], days)
        coord = data['city']['coord']
        return cards, data['city']['name'], data['city'].get('country', ''), coord['lat'], coord['lon']

    @classmethod
    def by_coords(cls, lat: float, lon: float, days: int = 7, units: str = 'metric') -> tuple[list, str, str, float, float]:
        """
        Query forecast using geographic coordinates.

        Returns:
          (cards, city_name, country_code, lat, lon)
        """
        data = cls._call({'lat': lat, 'lon': lon}, units=units)
        cards = parse_daily_forecasts(data['list'], days)
        return cards, data['city']['name'], data['city'].get('country', ''), lat, lon

    @classmethod
    def hourly_by_coords(cls, lat: float, lon: float, hours: int = 24, step: int = 3, units: str = "metric") -> list[dict]:
        """
        Returns next `hours` worth of temperature readings in `step`-hour intervals.

        Each entry: { dt: <unix timestamp>, temp: <int rounded temp> }
        """
        data = cls._call({"lat": lat, "lon": lon}, units=units)
        count = hours // step
        entries = data["list"][:count]

        return [
            {"dt": e["dt"], "temp": round(e["main"]["temp"])}
            for e in entries
        ]
