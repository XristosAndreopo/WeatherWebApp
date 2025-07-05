# File: weather/utils.py

"""
weather/utils.py

This module provides utility functions and data structures for:
  - Parsing and transforming OpenWeatherMap API responses.
  - Mapping weather descriptions to local icon filenames.
  - Fetching user preferences (unit, city, country).
"""

from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
from django.utils import timezone

from .constants import ICON_MAP, DEFAULT_ICON
from .models import Preference


@dataclass
class ForecastCard:
    """
    Represents a structured forecast object for a single day,
    used in HTML templates.

    Fields:
      - date (str): Formatted datetime ('YYYY-MM-DD HH:MM') in local time.
      - description (str): Weather condition (e.g., 'clear sky').
      - temp (int | None): Temperature in °C or °F, rounded.
      - humidity (int | None): Humidity percentage.
      - icon (str): Icon filename from /static/img/weather_icons/.
      - error (str): Optional error message for this card.
    """
    date: str = ''
    description: str = ''
    temp: int | None = None
    humidity: int | None = None
    icon: str = ''
    error: str = ''


def get_icon_for_description(desc: str) -> str:
    """
    Maps a weather description (e.g. 'clear sky') to a local icon filename.

    Args:
        desc (str): The raw weather description from OpenWeatherMap.

    Returns:
        str: The corresponding icon filename (e.g. 'clear.png').
             Falls back to DEFAULT_ICON if no match is found.
    """
    desc_lower = desc.lower()
    for key, icon in ICON_MAP.items():
        if key in desc_lower:
            return icon
    return DEFAULT_ICON


def parse_daily_forecasts(raw_list: list[dict], days: int = 7) -> list[ForecastCard]:
    """
    From a 5-day forecast (3-hour intervals), extract one representative sample per day.

    The logic:
    - Always return today’s forecast as the last sample or the first future sample.
    - Then return one future sample per day (up to `days` total).

    Args:
        raw_list (list[dict]): List of raw forecast dicts from OpenWeatherMap.
        days (int): Number of days to include (default: 7).

    Returns:
        list[ForecastCard]: A list of ForecastCard objects, one per calendar day.
    """
    now_local = timezone.now()
    today_key = now_local.strftime('%Y-%m-%d')

    by_date: dict[str, ForecastCard] = {}
    last_today: ForecastCard | None = None

    for item in raw_list:
        # 1. Convert UTC timestamp to timezone-aware datetime
        dt_utc = datetime.fromtimestamp(item['dt'], tz=dt_timezone.utc)

        # 2. Convert UTC → local timezone (based on Django's TIME_ZONE setting)
        dt_local = timezone.localtime(dt_utc)
        date_key = dt_local.strftime('%Y-%m-%d')

        # 3. Build ForecastCard for that 3-hour period
        card = ForecastCard(
            date=dt_local.strftime('%Y-%m-%d %H:%M'),
            description=item['weather'][0]['description'],
            temp=round(item['main']['temp']),
            humidity=item['main']['humidity'],
            icon=get_icon_for_description(item['weather'][0]['description']),
        )

        # Track latest available today sample
        if date_key == today_key:
            last_today = card

        # Store the first available sample for each future day
        if date_key not in by_date and dt_local >= now_local:
            by_date[date_key] = card

    results: list[ForecastCard] = []

    # Add today’s forecast (prefer future sample, else fallback)
    if today_key in by_date:
        results.append(by_date.pop(today_key))
    elif last_today:
        results.append(last_today)
    else:
        results.append(ForecastCard(error="No forecast available for today."))

    # Add next (days-1) forecasts
    for future_day in sorted(by_date.keys())[: days - 1]:
        results.append(by_date[future_day])

    return results


def get_user_pref(user) -> tuple[Preference, str]:
    """
    Retrieve or initialize the Preference row for a user.

    Args:
        user (User): The currently authenticated Django user.

    Returns:
        tuple[Preference, str]: A tuple containing:
          - The user’s Preference object.
          - The appropriate unit symbol ('°C' or '°F').
    """
    pref, _ = Preference.objects.get_or_create(user=user)
    symbol = '°F' if pref.default_unit == 'imperial' else '°C'
    return pref, symbol
