# tests/test_utils.py

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone as dt_timezone
from django.utils import timezone

from weather.utils import get_icon_for_description, parse_daily_forecasts, get_user_pref, ForecastCard
from weather.constants import DEFAULT_ICON, ICON_MAP

class UtilsTests(TestCase):
    def test_get_icon_for_description_matches_known_key(self):
        # Test that description containing a key returns its icon
        for key, icon in ICON_MAP.items():
            desc = f"Some {key} here"
            self.assertEqual(get_icon_for_description(desc), icon)

    def test_get_icon_for_description_fallback(self):
        # Test that unknown descriptions return the default icon
        self.assertEqual(get_icon_for_description("unusual weather"), DEFAULT_ICON)

    def test_parse_daily_forecasts_basic(self):
        # Create fake 3‑hour interval data for today and tomorrow
        now_utc = datetime.now(dt_timezone.utc)
        entries = []
        # Entry for today (future time)
        entries.append({
            'dt': int((now_utc + timedelta(hours=1)).timestamp()),
            'weather': [{'description': 'clear sky'}],
            'main': {'temp': 20.5, 'humidity': 55}
        })
        # Entry for tomorrow
        entries.append({
            'dt': int((now_utc + timedelta(days=1, hours=1)).timestamp()),
            'weather': [{'description': 'rain'}],
            'main': {'temp': 15.2, 'humidity': 65}
        })

        # Parse and check two forecasts returned
        cards = parse_daily_forecasts(entries, days=2)
        self.assertEqual(len(cards), 2)
        self.assertIsInstance(cards[0], ForecastCard)
        self.assertIsInstance(cards[1], ForecastCard)

    def test_get_user_pref_and_symbol_metric(self):
        # New user should get default unit symbol '°C'
        user = User.objects.create_user(username='test1', password='pass')
        pref, symbol = get_user_pref(user)
        self.assertEqual(symbol, '°C')
        self.assertEqual(pref.default_unit, 'metric')

    def test_get_user_pref_and_symbol_imperial(self):
        # Imperial user should get symbol '°F'
        user = User.objects.create_user(username='test2', password='pass')
        pref, _ = get_user_pref(user)
        pref.default_unit = 'imperial'
        pref.save()
        pref, symbol = get_user_pref(user)
        self.assertEqual(symbol, '°F')
        self.assertEqual(pref.default_unit, 'imperial')
