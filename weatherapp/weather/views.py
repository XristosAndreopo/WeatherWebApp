# File: weather/views.py

"""
weather/views.py

Django views for WeatherWebApp:
  - Class-based views for home, settings, find, map, favorites, about, contact, profile.
  - Function-based views for login, logout, and AJAX endpoints.
  - Improved login_view: returns validation errors to template for better UX.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout

from .forms import LocationSearchForm
from .models import FavoriteLocation
from .services import WeatherService, WeatherAPIError
from .utils import get_user_pref


class HomeView(TemplateView):
    """Dashboard view showing welcome message and weather quote."""
    template_name = 'weather/home.html'


class SettingsView(LoginRequiredMixin, TemplateView):
    """User settings: default city, country, units, and theme."""
    template_name = 'weather/settings.html'

    def get(self, request, *args, **kwargs):
        pref, _ = get_user_pref(request.user)
        return self.render_to_response({'preference': pref})

    def post(self, request, *args, **kwargs):
        pref, _ = get_user_pref(request.user)
        # Update user preferences from submitted form data
        pref.default_city    = request.POST.get('default_city', '').strip()
        pref.default_country = request.POST.get('default_country', '').strip().upper()
        pref.default_unit    = request.POST.get('default_unit', 'metric')
        pref.default_theme   = request.POST.get('default_theme', 'light')
        pref.save()
        messages.success(request, 'Preferences saved.')
        # Persist theme choice in a cookie for front-end theme manager
        resp = redirect('settings')
        resp.set_cookie('theme', pref.default_theme, max_age=365*24*3600)
        return resp


class FindLocationView(LoginRequiredMixin, TemplateView):
    """Handle “Find by Location” page: search form, daily/hourly forecasts."""
    template_name = 'weather/find_location.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pref, unit_symbol = get_user_pref(self.request.user)
        form = LocationSearchForm(self.request.GET or None)

        context.update({
            'preference': pref,
            'unit_symbol': unit_symbol,
            'form': form,
        })

        city_q    = self.request.GET.get('city', '').strip()
        country_q = self.request.GET.get('country', '').strip().upper()

        # Only run search when city is provided or a default exists
        if city_q or pref.default_city:
            context['searched'] = True
            try:
                cards, city_display, _, lat, lng = WeatherService.by_city(
                    city_q or pref.default_city,
                    country_q or pref.default_country or None,
                    units=pref.default_unit
                )
                context.update({
                    'weather': cards,
                    'city_display': city_display,
                    'find_lat': lat,
                    'find_lng': lng,
                })
            except WeatherAPIError as e:
                # Pass API error message into template
                context['error_message'] = str(e)
        else:
            context['searched'] = False

        return context


class MapView(LoginRequiredMixin, TemplateView):
    """Interactive map page – JS handles data fetching via AJAX."""
    template_name = 'weather/map.html'


class FavoritesView(LoginRequiredMixin, TemplateView):
    """Display and manage user's favorite locations with brief forecasts."""
    template_name = 'weather/favorites.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pref, unit_symbol = get_user_pref(self.request.user)
        favorites = []

        for fav in FavoriteLocation.objects.filter(user=self.request.user):
            try:
                # Fetch only today and tomorrow's forecasts
                cards, *_ = WeatherService.by_city(
                    fav.city_name, fav.country_code or None,
                    days=2,
                    units=pref.default_unit
                )
                today    = cards[0]
                tomorrow = cards[1] if len(cards) > 1 else cards[0]
            except WeatherAPIError as e:
                # Represent API failure in both slots
                today = tomorrow = type('E', (), {'error': str(e)})()

            favorites.append({
                'id': fav.id,
                'city': fav.city_name,
                'country': fav.country_code,
                'today': today,
                'tomorrow': tomorrow,
            })

        context.update({
            'unit_symbol': unit_symbol,
            'favorite_weather': favorites,
        })
        return context


@login_required
def map_weather_data(request):
    """
    AJAX endpoint for daily forecast.
    Returns JSON:
      {
        'forecast': [ {date, description, temp, humidity, icon, error}, … ],
        'location': 'City Name',
        'country': 'CC',
        'unit': '°C' or '°F'
      }
    """
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    try:
        # Get user’s unit preference (and symbol)
        pref, unit_symbol = get_user_pref(request.user)

        # Call the service and unpack its tuple
        cards, city, country, _, _ = WeatherService.by_coords(
            float(lat),
            float(lng),
            units=pref.default_unit
        )

        # Serialize dataclass instances to plain dicts
        forecast = [card.__dict__ for card in cards]

        return JsonResponse({
            'forecast': forecast,
            'location': city,
            'country': country,
            'unit':     unit_symbol,
        })
    except WeatherAPIError as e:
        # Known API errors: return JSON with error message
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        # Catch-all: avoid returning HTML error pages to the frontend
        return JsonResponse({'error': 'Server error: ' + str(e)}, status=500)

@login_required
def map_hourly_data(request):
    """
    AJAX endpoint for next‑24h hourly data.
    Returns JSON:
      {
        'hourly': [ {dt: 1234567890, temp: 23}, … ],
        'unit': '°C' or '°F'
      }
    """
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    try:
        pref, unit_symbol = get_user_pref(request.user)

        hourly = WeatherService.hourly_by_coords(
            float(lat),
            float(lng),
            units=pref.default_unit
        )

        return JsonResponse({
            'hourly': hourly,
            'unit':   unit_symbol,
        })

    except WeatherAPIError as e:
        return JsonResponse({'error': str(e)}, status=400)

    except Exception as e:
        return JsonResponse({'error': 'Server error: ' + str(e)}, status=500)

@login_required
def add_favorite(request):
    """
    Handle “Add to Favorites” form POST.
    Creates FavoriteLocation if not already exists.
    """
    if request.method == 'POST':
        city    = request.POST.get('city')
        country = request.POST.get('country') or None
        FavoriteLocation.objects.get_or_create(
            user=request.user,
            city_name=city,
            country_code=country
        )
        messages.success(request, f'{city} added to favorites.')
    # Redirect back to referring page (home/map/find)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def remove_favorite(request, favorite_id):
    """
    Handle “Remove” action for a favorite location.
    """
    FavoriteLocation.objects.filter(id=favorite_id, user=request.user).delete()
    messages.success(request, 'Favorite removed.')
    return redirect('favorites')


class AboutView(TemplateView):
    """Static “About” page."""
    template_name = 'weather/about.html'


class ContactView(TemplateView):
    """Contact form page – no custom POST handling (emails printed to console)."""
    template_name = 'weather/contact.html'


def login_view(request):
    """
    Custom login view:
      - Uses Django’s AuthenticationForm.
      - On failure, captures non-field errors and passes 'error' into template.
    """
    error = None

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
        else:
            # Extract authentication errors (e.g. invalid credentials)
            error = form.non_field_errors().as_text()
    else:
        form = AuthenticationForm(request)

    return render(request, 'weather/login.html', {
        'form': form,
        'error': error,
    })


def logout_view(request):
    """
    Log the user out and redirect to home.
    """
    logout(request)
    return redirect('home')


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile page (view-only)."""
    template_name = 'weather/profile.html'
