# File: weather/urls.py

"""
weather/urls.py

Defines route mappings for all views in the WeatherWebApp.

Structure:
  - Home & Static Pages
  - Settings & Search
  - Map + AJAX API endpoints
  - Favorites CRUD
  - User Authentication
"""

from django.urls import path
from . import views

urlpatterns = [

    # ───────────────────────────────────────────────────────────────────────────────
    # Core Dashboard & Static Pages
    # ───────────────────────────────────────────────────────────────────────────────
    path('',                    views.HomeView.as_view(),        name='home'),
    path('about/',              views.AboutView.as_view(),       name='about'),
    path('contact/',            views.ContactView.as_view(),     name='contact'),
    path('profile/',            views.ProfileView.as_view(),     name='profile'),

    # ───────────────────────────────────────────────────────────────────────────────
    # User Preferences & Location Search
    # ───────────────────────────────────────────────────────────────────────────────
    path('settings/',           views.SettingsView.as_view(),    name='settings'),
    path('find/',               views.FindLocationView.as_view(),name='find_location'),

    # ───────────────────────────────────────────────────────────────────────────────
    # Map + AJAX forecast endpoints
    # ───────────────────────────────────────────────────────────────────────────────
    path('map/',                views.MapView.as_view(),         name='map'),
    path('map_weather_data/',   views.map_weather_data,          name='map_weather_data'),
    path('map_hourly_data/',    views.map_hourly_data,           name='map_hourly_data'),

    # ───────────────────────────────────────────────────────────────────────────────
    # Favorite Locations (CRUD)
    # ───────────────────────────────────────────────────────────────────────────────
    path('favorites/',          views.FavoritesView.as_view(),   name='favorites'),
    path('add_favorite/',       views.add_favorite,              name='add_favorite'),
    path('remove_favorite/<int:favorite_id>/', views.remove_favorite, name='remove_favorite'),

    # ───────────────────────────────────────────────────────────────────────────────
    # Authentication (login/logout)
    # ───────────────────────────────────────────────────────────────────────────────
    path('login/',              views.login_view,                name='login'),
    path('logout/',             views.logout_view,               name='logout'),
]
