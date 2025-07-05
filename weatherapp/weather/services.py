# File: weather/services.py

"""
weather/services.py

Abstraction layer for calling the OpenWeatherMap API and transforming data into
templates-friendly structures.

Features:
  - by_city(city, country, …) → list of ForecastCard + location metadata
  - by_coords(lat, lon, …)
  - hourly_by_coords(lat, lon) → simplified hourly forecast entries
"""

import logging
from typing import Any, Dict, List, Tuple, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, Timeout
from urllib3.util.retry import Retry
from django.conf import settings

from .constants import OPENWEATHER_BASE
from .utils import parse_daily_forecasts, ForecastCard

# Set up module-level logger
logger = logging.getLogger(__name__)


class WeatherAPIError(Exception):
    """Custom exception for handling OpenWeatherMap API failures and network errors."""


class WeatherService:
    """
    API client wrapper for OpenWeatherMap 5-day/3-hour forecast endpoint.
    Uses a requests.Session with retry/backoff for resilience.

    Public methods:
      - by_city(city, country, days, units)
      - by_coords(lat, lon, days, units)
      - hourly_by_coords(lat, lon, hours, step, units)
    """

    # Shared Session configured with retries on transient failures
    _session: requests.Session = requests.Session()
    _session.mount(
        "https://",
        HTTPAdapter(
            max_retries=Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"],
            )
        ),
    )
    _session.mount("http://", HTTPAdapter(max_retries=Retry(total=3)))

    @staticmethod
    def _call(params: Dict[str, Any], units: str) -> Dict[str, Any]:
        """
        Internal helper to perform the HTTP GET to the OpenWeatherMap API.

        Parameters:
          - params: query parameters (e.g. {'q': 'London,GB'} or {'lat': 51.5, 'lon': -0.1})
          - units: 'metric' or 'imperial'

        Returns:
          - Parsed JSON response as dict.

        Raises:
          - WeatherAPIError: on HTTP errors, network failures, timeouts, or API error codes.
        """
        # Build payload with API key and units
        payload = {**params, 'appid': settings.OPENWEATHER_API_KEY, 'units': units}
        logger.debug("Requesting OpenWeatherMap: %s with %s", OPENWEATHER_BASE, payload)

        try:
            resp = WeatherService._session.get(OPENWEATHER_BASE, params=payload, timeout=10)
            resp.raise_for_status()
        except Timeout as e:
            logger.error("OpenWeatherMap request timed out: %s", e)
            raise WeatherAPIError("Weather service timed out, please try again later.")
        except RequestException as e:
            logger.error("Network error calling OpenWeatherMap: %s", e)
            raise WeatherAPIError(f"Network error: {e}")

        try:
            data = resp.json()
        except ValueError as e:
            logger.error("Invalid JSON from OpenWeatherMap: %s", e)
            raise WeatherAPIError("Invalid response from weather service.")

        # The API returns 'cod' as string or int on errors
        code = data.get('cod')
        if code not in (200, '200'):
            message = data.get('message', 'Unknown API error')
            logger.warning("OpenWeatherMap API error: cod=%s, message=%s", code, message)
            raise WeatherAPIError(message)

        return data

    @classmethod
    def by_city(
        cls,
        city: str,
        country: Optional[str] = None,
        days: int = 7,
        units: str = 'metric'
    ) -> Tuple[List[ForecastCard], str, str, float, float]:
        """
        Fetch daily forecasts by city name (and optional country code).

        Parameters:
          - city: city name, e.g. "London"
          - country: optional ISO 2-letter country code, e.g. "GB"
          - days: number of days to return (max 7)
          - units: 'metric' or 'imperial'

        Returns:
          - cards: list of ForecastCard, length up to `days`
          - city_name: normalized city name from API
          - country_code: ISO country code from API (may be empty)
          - lat, lon: float coordinates

        Raises:
          - WeatherAPIError on network/API failures.
        """
        query = f"{city},{country}" if country else city
        data = cls._call({'q': query}, units=units)

        coord = data['city']['coord']
        cards = parse_daily_forecasts(data['list'], days)

        return (
            cards,
            data['city']['name'],
            data['city'].get('country', ''),
            coord['lat'],
            coord['lon'],
        )

    @classmethod
    def by_coords(
        cls,
        lat: float,
        lon: float,
        days: int = 7,
        units: str = 'metric'
    ) -> Tuple[List[ForecastCard], str, str, float, float]:
        """
        Fetch daily forecasts by geographic coordinates.

        Parameters:
          - lat, lon: decimal latitude and longitude
          - days: number of days to return
          - units: 'metric' or 'imperial'

        Returns:
          - (cards, city_name, country_code, lat, lon)
        """
        data = cls._call({'lat': lat, 'lon': lon}, units=units)
        cards = parse_daily_forecasts(data['list'], days)

        return (
            cards,
            data['city']['name'],
            data['city'].get('country', ''),
            lat,
            lon,
        )

    @classmethod
    def hourly_by_coords(
        cls,
        lat: float,
        lon: float,
        hours: int = 24,
        step: int = 3,
        units: str = "metric"
    ) -> List[Dict[str, Any]]:
        """
        Fetch and return the next `hours` worth of data in `step`-hour increments.

        Parameters:
          - lat, lon: decimal latitude and longitude
          - hours: total hours of forecast (default 24)
          - step: interval in hours between samples (default 3)
          - units: 'metric' or 'imperial'

        Returns:
          - A list of dicts:
              [
                { 'dt': <unix timestamp>, 'temp': <int temperature> },
                ...
              ]
        """
        data = cls._call({"lat": lat, "lon": lon}, units=units)
        max_count = hours // step
        entries = data.get("list", [])[:max_count]

        hourly = []
        for entry in entries:
            timestamp = entry.get("dt")
            temp = entry.get("main", {}).get("temp")
            if timestamp is None or temp is None:
                logger.debug("Skipping invalid hourly entry: %s", entry)
                continue
            hourly.append({
                "dt": timestamp,
                "temp": round(temp),
            })

        return hourly
