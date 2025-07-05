# File: config/context_processors.py

"""
Injects the logged‑in user’s default_city and default_country
into every template context, by reading the Preference model
from the weather app.
"""

from django.contrib.auth.models import AnonymousUser
from weather.models import Preference    # ← import from your app, which is named "weather"

def user_preferences(request):
    """
    If the user is authenticated, get or create their Preference row
    and return its default_city/default_country in the context.
    Otherwise, return an empty dict.
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated or isinstance(user, AnonymousUser):
        return {}

    pref, _ = Preference.objects.get_or_create(user=user)
    return {
        'default_city': pref.default_city,
        'default_country': pref.default_country,
    }
