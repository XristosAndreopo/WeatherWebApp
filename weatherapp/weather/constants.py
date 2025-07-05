# File: weather/constants.py

"""
weather/constants.py

Centralized constants and configuration for the WeatherWebApp.

Responsibilities:
  • Specify where local weather icon images live (relative to STATIC_URL).
  • Map OpenWeatherMap “description” substrings to those icon filenames.
  • Provide a fallback icon if no description matches.
  • Declare environment-variable names for API integration.
  • Compute the OpenWeatherMap API base URL, overrideable via env var.
"""

import os
from typing import Mapping

# ───────────────────────────────────────────────────────────────────────────────
# STATIC ASSETS
# ───────────────────────────────────────────────────────────────────────────────

#: Directory (under STATIC_URL) where weather icons are stored.
ICON_DIR: str = 'img/weather_icons'

# ───────────────────────────────────────────────────────────────────────────────
# ICON MAP
# ───────────────────────────────────────────────────────────────────────────────

#: Map of substrings in the OWM "description" → local icon filename.
ICON_MAP: Mapping[str, str] = {
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

#: Fallback icon filename when no key in ICON_MAP matches.
DEFAULT_ICON: str = 'default.png'

# ───────────────────────────────────────────────────────────────────────────────
# ENVIRONMENT VARIABLE NAMES
# ───────────────────────────────────────────────────────────────────────────────

#: Environment variable name for the OpenWeatherMap API key.
OPENWEATHER_API_KEY_ENV: str  = 'OPENWEATHER_API_KEY'
#: Environment variable name for the forecast endpoint override.
OPENWEATHER_BASE_URL_ENV: str = 'OPENWEATHER_BASE_URL'

# ───────────────────────────────────────────────────────────────────────────────
# OPENWEATHERMAP ENDPOINT
# ───────────────────────────────────────────────────────────────────────────────

#: Base URL for the 5-day/3-hour forecast endpoint.
#: Can be overridden by setting OPENWEATHER_BASE_URL in the environment.
OPENWEATHER_BASE_URL: str = os.getenv(
    OPENWEATHER_BASE_URL_ENV,
    'https://api.openweathermap.org/data/2.5/forecast'
)

#: Legacy alias for backward compatibility.
OPENWEATHER_BASE: str = OPENWEATHER_BASE_URL
