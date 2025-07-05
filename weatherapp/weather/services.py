import requests
from django.conf import settings
from .constants import OPENWEATHER_BASE
from .utils import parse_daily_forecasts

class WeatherAPIError(Exception):
    """Raised on OpenWeatherMap API errors."""

class WeatherService:
    """Client for OpenWeatherMap free forecast endpoints."""

    @staticmethod
    def _call(params: dict, units: str) -> dict:
        payload = {
            **params,
            'appid': settings.OPENWEATHER_API_KEY,
            'units': units
        }
        resp = requests.get(OPENWEATHER_BASE, params=payload, timeout=10)
        data = resp.json()
        if data.get('cod') not in (200, '200'):
            raise WeatherAPIError(data.get('message', 'Unknown API error'))
        return data

    @classmethod
    def by_city(
        cls,
        city: str,
        country: str | None = None,
        days: int = 7,
        units: str = 'metric'
    ) -> tuple[list, str, str, float, float]:
        """
        Returns (cards, city_name, country_code, lat, lon).
        """
        q = f"{city},{country}" if country else city
        data = cls._call({'q': q}, units=units)
        cards = parse_daily_forecasts(data['list'], days)
        coord = data['city']['coord']
        return cards, data['city']['name'], data['city'].get('country', ''), coord['lat'], coord['lon']

    @classmethod
    def by_coords(
        cls,
        lat: float,
        lon: float,
        days: int = 7,
        units: str = 'metric'
    ) -> tuple[list, str, str, float, float]:
        """
        Returns (cards, city_name, country_code, lat, lon) for given coords.
        """
        data = cls._call({'lat': lat, 'lon': lon}, units=units)
        cards = parse_daily_forecasts(data['list'], days)
        return cards, data['city']['name'], data['city'].get('country', ''), lat, lon

    @classmethod
    def hourly_by_coords(
        cls,
        lat: float,
        lon: float,
        hours: int = 24,
        step: int = 3,
        units: str = "metric",
    ) -> list[dict]:
        """
        Fetch 5‑day /forecast and return the next `hours` of data
        in `step`‑hour increments.
        """
        data = cls._call({"lat": lat, "lon": lon}, units=units)
        count = hours // step
        entries = data["list"][:count]
        return [
            {"dt": e["dt"], "temp": round(e["main"]["temp"])}
            for e in entries
        ]
