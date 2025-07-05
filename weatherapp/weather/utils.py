# File: weather/utils.py

"""
weather/utils.py

Utility functions for parsing OpenWeatherMap data and user preferences.

Responsibilities:
  - ForecastCard: a dataclass representing a single day’s forecast for templating.
  - get_icon_for_description: map OWM descriptions to local filenames.
  - parse_daily_forecasts: pick one sample per calendar day (today + next days),
      using timezone-aware datetimes.
  - get_user_pref: fetch or create the user's Preference row and unit symbol.
"""

from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone

from django.utils import timezone
from .constants import ICON_MAP, DEFAULT_ICON
from .models import Preference  # your app is named "weather"


@dataclass
class ForecastCard:
    """
    Structured data for a single forecast card in your templates.
    Attributes:
      - date: 'YYYY-MM-DD HH:MM' in local time.
      - description: raw text from the API.
      - temp: rounded integer temperature.
      - humidity: integer humidity percent.
      - icon: filename chosen by get_icon_for_description().
      - error: non-empty if something went wrong (e.g. no data).
    """
    date: str = ''
    description: str = ''
    temp: int | None = None
    humidity: int | None = None
    icon: str = ''
    error: str = ''


def get_icon_for_description(desc: str) -> str:
    """
    Map an OpenWeather `description` substring to a local icon filename.
    Falls back to DEFAULT_ICON if no key matches.
    """
    lower = desc.lower()
    for key, icon in ICON_MAP.items():
        if key in lower:
            return icon
    return DEFAULT_ICON


def parse_daily_forecasts(raw_list: list[dict], days: int = 7) -> list[ForecastCard]:
    """
    From the 3‑hourly `raw_list` (5‑day forecast), pick one sample per day up to `days`.
    Always include today’s last available or next future sample, then subsequent days.

    Algorithm:
      1. now = current local time (aware) via django.utils.timezone.now()
      2. Iterate each `item`:
         a. Convert UNIX timestamp to an aware UTC datetime.
         b. Convert that UTC datetime into the local timezone.
         c. Use its date string (YYYY‑MM‑DD) as the grouping key.
         d. Track the last sample for today, and the first future sample per subsequent day.
      3. Build results:
         - Today’s card: prefer future sample, else last‑seen today, else an error card.
         - Next (days‑1) cards in chronological order.
    """
    now_local = timezone.now()
    today_key = now_local.strftime('%Y-%m-%d')

    by_date: dict[str, ForecastCard] = {}
    last_today: ForecastCard | None = None

    for item in raw_list:
        # 1) Create an aware UTC datetime from the timestamp
        dt_utc = datetime.fromtimestamp(item['dt'], tz=dt_timezone.utc)
        # 2) Convert to local timezone (so date grouping matches YOUR TIME_ZONE)
        dt_local = timezone.localtime(dt_utc)
        key = dt_local.strftime('%Y-%m-%d')

        card = ForecastCard(
            date=dt_local.strftime('%Y-%m-%d %H:%M'),
            description=item['weather'][0]['description'],
            temp=round(item['main']['temp']),
            humidity=item['main']['humidity'],
            icon=get_icon_for_description(item['weather'][0]['description'])
        )

        if key == today_key:
            # Keep overwriting so last_today ends up as the latest sample for today
            last_today = card

        # Register the first future sample per date (including today if dt_local > now_local)
        if key not in by_date and dt_local >= now_local:
            by_date[key] = card

    results: list[ForecastCard] = []

    # --- Today’s card ---
    if today_key in by_date:
        results.append(by_date.pop(today_key))
    elif last_today:
        results.append(last_today)
    else:
        results.append(ForecastCard(error='No forecast data for today.'))

    # --- Subsequent days ---
    for date_str in sorted(by_date.keys())[: days - 1]:
        results.append(by_date[date_str])

    return results


def get_user_pref(user) -> tuple[Preference, str]:
    """
    Retrieve or create the user's Preference row.
    Returns (pref, unit_symbol) where unit_symbol is '°C' or '°F'.
    """
    pref, _ = Preference.objects.get_or_create(user=user)
    symbol = '°F' if pref.default_unit == 'imperial' else '°C'
    return pref, symbol
