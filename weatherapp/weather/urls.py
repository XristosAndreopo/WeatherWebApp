"""weather/urls.py - URL routes for the weather app"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Dashboard
    path('settings/', views.settings_view, name='settings'),
    path('find/', views.find_location, name='find_location'),
    path('add_favorite/', views.add_favorite, name='add_favorite'),
    path('favorites/', views.favorites, name='favorites'),
    path('remove_favorite/<int:favorite_id>/', views.remove_favorite, name='remove_favorite'),
    path('map/', views.map_view, name='map'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('map_weather_data/', views.map_weather_data, name='map_weather_data'),
    # Authentication URLs (use Django's built-in)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]
