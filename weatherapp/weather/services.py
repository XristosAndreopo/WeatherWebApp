import requests
from django.conf import settings
from .constants import OPENWEATHER_BASE
from .utils import parse_daily_forecasts

class WeatherAPIError(Exception):
    """Raised when the OpenWeatherMap API returns an error or non-200 code."""

class WeatherService:
    """
    WeatherService wraps calls to OpenWeatherMap:
      - by_city:   forecast by city name
      - by_coords: forecast by latitude/longitude
    Both return a list of ForecastCard dataclasses plus city/country info.
    """

    @staticmethod
    def _call(params: dict, units: str) -> dict:
        """
        Internal helper to invoke the forecast endpoint.

        :param params: Query parameters (e.g. {'q': 'London,GB'} or {'lat': 51.5, 'lon': -0.1})
        :param units: 'metric' or 'imperial'
        :return: Parsed JSON
        :raises WeatherAPIError: on API error
        """
        payload = params.copy()
        payload['appid'] = settings.OPENWEATHER_API_KEY
        payload['units'] = units

        response = requests.get(OPENWEATHER_BASE, params=payload, timeout=10)
        data = response.json()
        # API returns cod as int or str
        if data.get('cod') not in (200, '200'):
            raise WeatherAPIError(data.get('message', 'Unknown API error'))
        return data

    @classmethod
    def by_city(cls, city: str, country: str | None = None,
                days: int = 7, units: str = 'metric'):
        """
        Get daily forecasts by city name.

        :param city: e.g. 'London'
        :param country: e.g. 'GB'
        :param days: number of days (max 7)
        :param units: 'metric' or 'imperial'
        :return: (list of ForecastCard, city_name, country_code)
        """
        query = f"{city},{country}" if country else city
        data = cls._call({'q': query}, units=units)
        cards = parse_daily_forecasts(data['list'], days)
        return cards, data['city']['name'], data['city'].get('country', '')

    @classmethod
    def by_coords(cls, lat: float, lon: float,
                  days: int = 7, units: str = 'metric'):
        """
        Get daily forecasts by geographic coordinates.

        :param lat: latitude
        :param lon: longitude
        :param days: number of days
        :param units: 'metric' or 'imperial'
        :return: (list of ForecastCard, city_name, country_code)
        """
        data = cls._call({'lat': lat, 'lon': lon}, units=units)
        cards = parse_daily_forecasts(data['list'], days)
        return cards, data['city']['name'], data['city'].get('country', '')
