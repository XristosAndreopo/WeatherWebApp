# File: weather/constants.py

"""
weather/constants.py

Central constants for OpenWeatherMap integration:
  - ICON_MAP: description→filename mapping for local icons.
  - DEFAULT_ICON: fallback image.
  - OPENWEATHER_BASE: the forecast endpoint base URL.
"""

import os

# Map key substrings in the API’s 'description' to local icon filenames
ICON_MAP = {
    'clear':           'clear.png',
    'few clouds':      'few_clouds.png',
    'scattered clouds':'scattered_clouds.png',
    'broken clouds':   'broken_clouds.png',
    'shower rain':     'shower_rain.png',
    'rain':            'rain.png',
    'thunderstorm':    'thunderstorm.png',
    'snow':            'snow.png',
    'mist':            'mist.png',
}

# If no ICON_MAP key matches, fall back to this
DEFAULT_ICON = 'default.png'

# Base URL for the 5-day / 3-hour forecast API
OPENWEATHER_BASE = os.environ.get(
    'OPENWEATHER_BASE_URL',
    'https://api.openweathermap.org/data/2.5/forecast'
)
