# File: tests/test_context_processors.py

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from config.context_processors import user_preferences
from weather.models import Preference

class UserPreferencesContextProcessorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_anonymous_user_returns_empty(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        context = user_preferences(request)
        self.assertEqual(context, {}, "Anonymous users should receive an empty context.")

    def test_authenticated_user_auto_created_preference_and_returns_defaults(self):
        # Create a new user; the post_save signal already creates the Preference
        user = User.objects.create_user(username='alice', password='pass')
        request = self.factory.get('/')
        request.user = user

        # Preference should already exist
        self.assertTrue(Preference.objects.filter(user=user).exists())

        context = user_preferences(request)

        # Fetch the auto‑created Preference
        pref = Preference.objects.get(user=user)
        self.assertEqual(pref.default_city, '', "Default city should be empty string")
        self.assertEqual(pref.default_country, '', "Default country should be empty string")

        # Context should reflect those defaults
        self.assertEqual(context, {
            'default_city': '',
            'default_country': ''
        })

    def test_authenticated_user_with_custom_preference(self):
        user = User.objects.create_user(username='bob', password='pass')
        # Retrieve and update the existing Preference
        pref = Preference.objects.get(user=user)
        pref.default_city = 'Paris'
        pref.default_country = 'FR'
        pref.save()

        request = self.factory.get('/')
        request.user = user

        context = user_preferences(request)
        self.assertEqual(context, {
            'default_city': 'Paris',
            'default_country': 'FR'
        })

    def test_idempotent_preference_creation(self):
        user = User.objects.create_user(username='eve', password='pass')
        request = self.factory.get('/')
        request.user = user

        # First call (Preference already exists due to signal)
        ctx1 = user_preferences(request)
        count_after_first = Preference.objects.filter(user=user).count()

        # Second call should not create another row
        ctx2 = user_preferences(request)
        count_after_second = Preference.objects.filter(user=user).count()

        self.assertEqual(count_after_first, 1)
        self.assertEqual(count_after_second, 1)
        self.assertEqual(ctx1, ctx2)
