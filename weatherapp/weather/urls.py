"""weather/urls.py - URL routes for the weather app"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.home, name='home'),

    # User settings
    path('settings/', views.settings_view, name='settings'),

    # “Find by Location”
    path('find/', views.find_location, name='find_location'),

    # Interactive map & its AJAX endpoints
    path('map/', views.map_view, name='map'),
    path('map_weather_data/', views.map_weather_data, name='map_weather_data'),

    # **New**: Next‑24‑hours endpoint for Chart.js on the map
    path('map_hourly_data/', views.map_hourly_data, name='map_hourly_data'),

    # Favorites CRUD
    path('add_favorite/', views.add_favorite, name='add_favorite'),
    path('favorites/', views.favorites, name='favorites'),
    path('remove_favorite/<int:favorite_id>/', views.remove_favorite, name='remove_favorite'),

    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]
