from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class FavoriteLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    city_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.country_code:
            return f"{self.city_name}, {self.country_code}"
        return self.city_name

class Preference(models.Model):
    """Per-user preferences: default location & units."""
    UNITS_CHOICES = [
        ('metric', 'Metric (°C)'),
        ('imperial', 'Imperial (°F)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preference')
    default_city = models.CharField(max_length=100, blank=True)
    default_country = models.CharField(max_length=10, blank=True)
    default_unit = models.CharField(max_length=10, choices=UNITS_CHOICES, default='metric')

    def __str__(self):
        return f"{self.user.username} Preferences"

@receiver(post_save, sender=User)
def create_user_preference(sender, instance, created, **kwargs):
    if created:
        Preference.objects.create(user=instance)