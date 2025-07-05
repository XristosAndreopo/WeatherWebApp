# File: weather/constants.py

"""
weather/constants.py

Shared constants used throughout the weather app, particularly for:
  - Mapping OpenWeatherMap weather descriptions to local icon images.
  - Providing a fallback icon for unmatched cases.
  - Defining the base URL for the 5-day forecast API.
"""

import os

# ───────────────────────────────────────────────────────────────────────────────
# WEATHER ICON MAPPING
# These substrings (from OpenWeatherMap's 'description') map to icon filenames.
# The frontend uses these icons from: /static/img/weather_icons/
# ───────────────────────────────────────────────────────────────────────────────
ICON_MAP = {
    'clear':             'clear.png',
    'few clouds':        'few_clouds.png',
    'scattered clouds':  'scattered_clouds.png',
    'broken clouds':     'broken_clouds.png',
    'shower rain':       'shower_rain.png',
    'rain':              'rain.png',
    'thunderstorm':      'thunderstorm.png',
    'snow':              'snow.png',
    'mist':              'mist.png',
}

# ───────────────────────────────────────────────────────────────────────────────
# Default icon filename to use when no ICON_MAP match is found
# ───────────────────────────────────────────────────────────────────────────────
DEFAULT_ICON = 'default.png'

# ───────────────────────────────────────────────────────────────────────────────
# Base URL for 5-day/3-hour OpenWeatherMap forecast endpoint
# You can override via an environment variable OPENWEATHER_BASE_URL
# ───────────────────────────────────────────────────────────────────────────────
OPENWEATHER_BASE = os.environ.get(
    'OPENWEATHER_BASE_URL',
    'https://api.openweathermap.org/data/2.5/forecast'
)
