# File: weather/urls.py

"""
weather/urls.py

URL routing for the WeatherWebApp.

Sections:
  • Public pages (home, about, contact, profile)
  • User settings & search UI (settings, find by location, interactive map)
  • AJAX endpoints (daily & hourly map data)
  • Favorites management (add, list, remove)
  • Authentication (login, logout)
"""

from django.urls import path
from . import views

urlpatterns = [
    # ───────────────────────────────────────────────────────────────────────────
    # Public / Static pages
    # ───────────────────────────────────────────────────────────────────────────
    path('',                      views.HomeView.as_view(),        name='home'),
    path('about/',                views.AboutView.as_view(),       name='about'),
    path('contact/',              views.ContactView.as_view(),     name='contact'),
    path('profile/',              views.ProfileView.as_view(),     name='profile'),

    # ───────────────────────────────────────────────────────────────────────────
    # User settings & search UI
    # ───────────────────────────────────────────────────────────────────────────
    path('settings/',             views.SettingsView.as_view(),    name='settings'),
    path('find/',                 views.FindLocationView.as_view(),name='find_location'),
    path('map/',                  views.MapView.as_view(),         name='map'),

    # ───────────────────────────────────────────────────────────────────────────
    # AJAX endpoints (JSON responses) for interactive map
    # ───────────────────────────────────────────────────────────────────────────
    path('map_weather_data/',     views.map_weather_data,          name='map_weather_data'),
    path('map_hourly_data/',      views.map_hourly_data,           name='map_hourly_data'),

    # ───────────────────────────────────────────────────────────────────────────
    # Favorites management
    # ───────────────────────────────────────────────────────────────────────────
    path('add_favorite/',         views.add_favorite,              name='add_favorite'),
    path('favorites/',            views.FavoritesView.as_view(),   name='favorites'),
    path('remove_favorite/<int:favorite_id>/', views.remove_favorite, name='remove_favorite'),

    # ───────────────────────────────────────────────────────────────────────────
    # Change Password
    # ───────────────────────────────────────────────────────────────────────────
    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # ───────────────────────────────────────────────────────────────────────────
    # Forgot Password
    # ───────────────────────────────────────────────────────────────────────────
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # ───────────────────────────────────────────────────────────────────────────
    # Sign‐up
    # ───────────────────────────────────────────────────────────────────────────
    path('signup/', views.signup_view, name='signup'),

    # ───────────────────────────────────────────────────────────────────────────
    # Authentication
    # ───────────────────────────────────────────────────────────────────────────
    path('login/',                views.login_view,                name='login'),
    path('logout/',               views.logout_view,               name='logout'),

]
