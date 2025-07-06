"""
config/context_processors.py

Context processor to expose a user’s preference defaults (city & country)
to every template’s context. If the user is not authenticated, returns {}.

Usage:
1. In settings.py, under TEMPLATES.OPTIONS.context_processors, include:
       'config.context_processors.user_preferences'
2. In any template, you can then use:
       {{ default_city }} and {{ default_country }}
"""

from typing import Dict
from django.contrib.auth.models import AnonymousUser
from weather.models import Preference


def user_preferences(request) -> Dict[str, str]:
    """
    Return a dict containing 'default_city' and 'default_country' for
    authenticated users, creating a Preference record on first access.
    Returns an empty dict for anonymous or unauthenticated requests.

    Args:
        request (HttpRequest): The current request object.

    Returns:
        dict: {
            'default_city': str,    # e.g. 'Athens' or ''
            'default_country': str, # e.g. 'GR' or ''
        }
        Or {} if request.user is not authenticated.
    """
    # Safely fetch the user attribute (might be None)
    user = getattr(request, 'user', None)

    # If there's no user, or they're not logged in, or it's an AnonymousUser, bail out
    if not user or not user.is_authenticated or isinstance(user, AnonymousUser):
        return {}

    # Get or create the Preference object for this user (auto‑creates on first call)
    preference, created = Preference.objects.get_or_create(user=user)

    # Inject only the two fields we care about
    return {
        'default_city': preference.default_city,
        'default_country': preference.default_country,
    }
