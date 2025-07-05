# File: weather/urls.py

"""
weather/urls.py

URL routing for the WeatherWebApp:
  - Class-based views: home, settings, find, map, favorites, about, contact, profile.
  - Function-based endpoints: login, logout, AJAX data, add/remove favorites.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard and static pages
    path('',                    views.HomeView.as_view(),        name='home'),
    path('about/',              views.AboutView.as_view(),       name='about'),
    path('contact/',            views.ContactView.as_view(),     name='contact'),
    path('profile/',            views.ProfileView.as_view(),     name='profile'),

    # User settings & search
    path('settings/',           views.SettingsView.as_view(),    name='settings'),
    path('find/',               views.FindLocationView.as_view(),name='find_location'),
    path('map/',                views.MapView.as_view(),         name='map'),

    # AJAX endpoints for map data
    path('map_weather_data/',   views.map_weather_data,          name='map_weather_data'),
    path('map_hourly_data/',    views.map_hourly_data,           name='map_hourly_data'),

    # Favorites management
    path('add_favorite/',       views.add_favorite,              name='add_favorite'),
    path('favorites/',          views.FavoritesView.as_view(),   name='favorites'),
    path('remove_favorite/<int:favorite_id>/', views.remove_favorite, name='remove_favorite'),

    # Authentication
    path('login/',              views.login_view,                name='login'),
    path('logout/',             views.logout_view,               name='logout'),
]
