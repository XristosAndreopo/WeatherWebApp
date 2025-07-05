# File: weather/models.py

"""
weather/models.py

Database models for:
  - FavoriteLocation: User's saved cities.
  - Preference: User-specific settings for city, units, theme.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class FavoriteLocation(models.Model):
    """
    Represents a saved favorite location per user.
    Stored data:
      - city_name (e.g. 'Athens')
      - optional country_code (e.g. 'GR')
      - user (ForeignKey)
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        help_text="The user who saved this location."
    )

    city_name = models.CharField(
        max_length=100,
        help_text="Name of the city, e.g. 'London'."
    )

    country_code = models.CharField(
        max_length=10,
        blank=True,
        help_text="Optional 2-letter ISO country code, e.g. 'GB'."
    )

    date_added = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this favorite was added."
    )

    def __str__(self):
        return f"{self.city_name}, {self.country_code}" if self.country_code else self.city_name


class Preference(models.Model):
    """
    Per-user settings that control search defaults and UI appearance.

    Includes:
      - default_city / default_country (e.g. 'Chania', 'GR')
      - default_unit: metric (°C) or imperial (°F)
      - default_theme: theme string (used in HTML and theme.js)
    """

    UNITS_CHOICES = [
        ('metric', 'Metric (°C)'),
        ('imperial', 'Imperial (°F)'),
    ]

    THEME_CHOICES = [
        ('light', 'Light'),
        ('light-dark', 'Light Dark'),
        ('dracula', 'Dracula'),
        ('high-contrast', 'High Contrast'),
        ('sepia', 'Sepia'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preference',
        help_text="The user this preference set belongs to."
    )

    default_city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City to auto-load when no search term is given."
    )

    default_country = models.CharField(
        max_length=10,
        blank=True,
        help_text="Optional ISO country code to pair with default_city."
    )

    default_unit = models.CharField(
        max_length=10,
        choices=UNITS_CHOICES,
        default='metric',
        help_text="Temperature unit: metric (°C) or imperial (°F)."
    )

    default_theme = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='light',
        help_text="Visual theme applied on first page load."
    )

    def __str__(self):
        return f"{self.user.username} Preferences"


@receiver(post_save, sender=User)
def create_user_preference(sender, instance, created, **kwargs):
    """
    Automatically creates a Preference row when a new User is created.
    """
    if created:
        Preference.objects.create(user=instance)
