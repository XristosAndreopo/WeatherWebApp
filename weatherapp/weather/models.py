from django.db import models
from django.contrib.auth.models import User

class FavoriteLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    city_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.country_code:
            return f"{self.city_name}, {self.country_code}"
        return self.city_name

