# File: weather/views.py

"""
weather/views.py

Contains Django views for the WeatherWebApp.
This file handles both UI rendering and JSON endpoints.

Modules:
- Class-based views (CBVs) for templates: Home, Settings, Find, Map, Favorites, etc.
- Function-based views (FBVs) for login, logout, AJAX calls, and favorites management.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth import login as auth_login
from .forms import LocationSearchForm
from .models import FavoriteLocation
from .services import WeatherService, WeatherAPIError
from .utils import get_user_pref
from .forms import SignUpForm
from django.contrib.auth.views import (
    PasswordChangeView as DjangoPasswordChangeView,
    PasswordChangeDoneView as DjangoPasswordChangeDoneView,
)
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView    as DjangoPasswordResetView,
    PasswordResetDoneView    as DjangoPasswordResetDoneView,
    PasswordResetConfirmView as DjangoPasswordResetConfirmView,
    PasswordResetCompleteView as DjangoPasswordResetCompleteView,
)

# ─────────────────────────────────────────────────────────────────────────────
# Class-Based Views (for rendering HTML pages)
# ─────────────────────────────────────────────────────────────────────────────

class HomeView(TemplateView):
    """Homepage: welcome message, intro card, and weather quotes."""
    template_name = 'weather/home.html'


class SettingsView(LoginRequiredMixin, TemplateView):
    """
    Handles user settings:
    - Default city, country, temperature unit (C/F), and theme preference.
    - Saves values to `Preference` model.
    """
    template_name = 'weather/settings.html'

    def get(self, request, *args, **kwargs):
        preference, _ = get_user_pref(request.user)
        return self.render_to_response({'preference': preference})

    def post(self, request, *args, **kwargs):
        preference, _ = get_user_pref(request.user)
        preference.default_city = request.POST.get('default_city', '').strip()
        preference.default_country = request.POST.get('default_country', '').strip().upper()
        preference.default_unit = request.POST.get('default_unit', 'metric')
        preference.default_theme = request.POST.get('default_theme', 'light')
        preference.save()

        messages.success(request, "Preferences updated successfully.")
        response = redirect('settings')
        response.set_cookie('theme', preference.default_theme, max_age=365 * 24 * 3600)
        return response


class FindLocationView(LoginRequiredMixin, TemplateView):
    """
    View for searching weather by city/country.
    - Uses GET parameters or user preferences.
    - Displays 7-day forecast cards.
    """
    template_name = 'weather/find_location.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pref, unit_symbol = get_user_pref(self.request.user)
        form = LocationSearchForm(self.request.GET or None)

        context.update({
            'form': form,
            'preference': pref,
            'unit_symbol': unit_symbol,
        })

        city_q = self.request.GET.get('city', '').strip()
        country_q = self.request.GET.get('country', '').strip().upper()

        if city_q or pref.default_city:
            try:
                cards, city_name, _, lat, lng = WeatherService.by_city(
                    city_q or pref.default_city,
                    country_q or pref.default_country or None,
                    units=pref.default_unit
                )
                context.update({
                    'searched': True,
                    'weather': cards,
                    'city_display': city_name,
                    'find_lat': lat,
                    'find_lng': lng,
                })
            except WeatherAPIError as e:
                context.update({
                    'searched': True,
                    'error_message': str(e)
                })
        else:
            context['searched'] = False

        return context


class MapView(LoginRequiredMixin, TemplateView):
    """
    Displays an interactive Leaflet map.
    JavaScript on this page handles search, rendering forecasts, and AJAX.
    """
    template_name = 'weather/map.html'


class FavoritesView(LoginRequiredMixin, TemplateView):
    """
    Renders the Favorites page, showing a 2-day forecast (today/tomorrow)
    for each saved favorite location.
    """
    template_name = 'weather/favorites.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pref, unit_symbol = get_user_pref(self.request.user)
        favorites_data = []

        for fav in FavoriteLocation.objects.filter(user=self.request.user):
            try:
                cards, *_ = WeatherService.by_city(
                    fav.city_name,
                    fav.country_code or None,
                    days=2,
                    units=pref.default_unit
                )
                today = cards[0]
                tomorrow = cards[1] if len(cards) > 1 else cards[0]
            except WeatherAPIError as e:
                error_card = type('ErrorCard', (), {'error': str(e)})
                today = tomorrow = error_card()

            favorites_data.append({
                'id': fav.id,
                'city': fav.city_name,
                'country': fav.country_code,
                'today': today,
                'tomorrow': tomorrow,
            })

        context.update({
            'unit_symbol': unit_symbol,
            'favorite_weather': favorites_data,
        })
        return context


class AboutView(TemplateView):
    """Static “About” page describing the app."""
    template_name = 'weather/about.html'


class ContactView(TemplateView):
    """Static contact form (prints to console during development)."""
    template_name = 'weather/contact.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile overview (non-editable for now)."""
    template_name = 'weather/profile.html'


# ─────────────────────────────────────────────────────────────────────────────
# AJAX Views – JSON endpoints for map/weather functionality
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def map_weather_data(request):
    """
    Returns daily forecast for map coordinates as JSON.
    Expects: GET lat & lng
    Response:
      {
        'forecast': [card, card, …],
        'location': 'City',
        'country': 'GR',
        'unit': '°C'
      }
    """
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        pref, unit_symbol = get_user_pref(request.user)

        cards, city, country, _, _ = WeatherService.by_coords(
            lat, lng, units=pref.default_unit
        )
        forecast_data = [card.__dict__ for card in cards]

        return JsonResponse({
            'forecast': forecast_data,
            'location': city,
            'country': country,
            'unit': unit_symbol
        })

    except WeatherAPIError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {e}'}, status=500)


@login_required
def map_hourly_data(request):
    """
    Returns next 24 hours of forecast as JSON.
    Expects: GET lat & lng
    Response:
      {
        'hourly': [{dt, temp}, …],
        'unit': '°C'
      }
    """
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        pref, unit_symbol = get_user_pref(request.user)

        hourly_data = WeatherService.hourly_by_coords(
            lat, lng, units=pref.default_unit
        )

        return JsonResponse({
            'hourly': hourly_data,
            'unit': unit_symbol
        })

    except WeatherAPIError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {e}'}, status=500)


# ─────────────────────────────────────────────────────────────────────────────
# Favorites (Add/Remove)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def add_favorite(request):
    """
    Adds a new FavoriteLocation from POST data.
    If the city is already saved by the user, does nothing.
    """
    if request.method == 'POST':
        city = request.POST.get('city')
        country = request.POST.get('country') or None
        FavoriteLocation.objects.get_or_create(
            user=request.user,
            city_name=city,
            country_code=country
        )
        messages.success(request, f'{city} added to favorites.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def remove_favorite(request, favorite_id):
    """
    Deletes a favorite location by ID (if owned by user).
    """
    FavoriteLocation.objects.filter(
        id=favorite_id,
        user=request.user
    ).delete()
    messages.success(request, 'Favorite removed.')
    return redirect('favorites')


# ─────────────────────────────────────────────────────────────────────────────
# Authentication Views
# ─────────────────────────────────────────────────────────────────────────────

def login_view(request):
    """
    Custom login with error handling.
    Returns login.html with error message if invalid credentials.
    """
    error = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
        error = form.non_field_errors().as_text()
    else:
        form = AuthenticationForm()
    return render(request, 'weather/login.html', {
        'form': form,
        'error': error
    })


def logout_view(request):
    """
    Log out user and redirect to home.
    """
    logout(request)
    return redirect('home')

# ─────────────────────────────────────────────────────────────────────────────
# NEW: Sign‑Up View
# ─────────────────────────────────────────────────────────────────────────────
def signup_view(request):
    """
    Render a sign-up form and create a new user.
    On successful POST, logs them in, adds a success message, and redirects to home.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Account created — you’re now signed in!")
            return redirect('home')   # <-- This must run on valid form
    else:
        form = SignUpForm()

    return render(request, 'weather/signup.html', {'form': form})

# ─────────────────────────────────────────────────────────────────────────────
# NEW: Change password in profile
# ─────────────────────────────────────────────────────────────────────────────

class PasswordChangeView(LoginRequiredMixin, DjangoPasswordChangeView):
    """
    Renders the password-change form and, on success, redirects to
    the ‘done’ page and shows a success message.
    """
    template_name = 'weather/password_change_form.html'
    success_url   = reverse_lazy('password_change_done')

    # you can override form_class if you want to customize fields/labels


class PasswordChangeDoneView(LoginRequiredMixin, DjangoPasswordChangeDoneView):
    """
    Simple confirmation page after password has been changed.
    """
    template_name = 'weather/password_change_done.html'

# ─────────────────────────────────────────────────────────────────────────────
# NEW: Change password in login if forgot
# ─────────────────────────────────────────────────────────────────────────────

class PasswordResetView(DjangoPasswordResetView):
    template_name            = 'weather/password_reset_form.html'
    email_template_name      = 'weather/password_reset_email.html'
    subject_template_name    = 'weather/password_reset_subject.txt'
    success_url              = reverse_lazy('password_reset_done')

class PasswordResetDoneView(DjangoPasswordResetDoneView):
    template_name = 'weather/password_reset_done.html'

class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    template_name = 'weather/password_reset_confirm.html'
    success_url   = reverse_lazy('password_reset_complete')

class PasswordResetCompleteView(DjangoPasswordResetCompleteView):
    template_name = 'weather/password_reset_complete.html'