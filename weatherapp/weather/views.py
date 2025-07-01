# weatherapp/weather/views.py

import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from .models import FavoriteLocation, Preference
from .services import WeatherService, WeatherAPIError


def home(request):
    """Dashboard/home page."""
    return render(request, 'weather/home.html')


@login_required
def settings_view(request):
    """
    GET: Show settings form with current preferences.
    POST: Save defaults (city, country, unit, theme), set theme cookie, then redirect.
    """
    pref, _ = Preference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        pref.default_city    = request.POST.get('default_city', '').strip()
        pref.default_country = request.POST.get('default_country', '').strip().upper()
        pref.default_unit    = request.POST.get('default_unit', 'metric')
        pref.default_theme   = request.POST.get('default_theme', 'light')
        pref.save()

        messages.success(request, 'Preferences saved.')
        response = redirect('settings')
        response.set_cookie('theme', pref.default_theme, max_age=365*24*3600)
        return response

    return render(request, 'weather/settings.html', {
        'preference': pref
    })


@login_required
def find_location(request):
    """
    Handle weather search by city/country or fallback to defaults.
    Pass daily forecast and coords for hourly chart.
    """
    pref, _ = Preference.objects.get_or_create(user=request.user)

    city_q    = request.GET.get('city', '').strip()
    country_q = request.GET.get('country', '').strip().upper()

    if city_q:
        city, country = city_q, (country_q or None)
        searched = True
    elif pref.default_city:
        city, country = pref.default_city, (pref.default_country or None)
        searched = True
    else:
        city = country = None
        searched = False

    weather = city_display = error_message = None
    find_lat = find_lng = None

    if searched and city:
        try:
            # by_city returns (cards, city_name, country_code, lat, lon)
            cards, city_display, _, find_lat, find_lng = WeatherService.by_city(
                city,
                country,
                days=7,
                units=pref.default_unit
            )
            weather = cards
        except WeatherAPIError as e:
            error_message = str(e)

    unit_symbol = '°F' if pref.default_unit == 'imperial' else '°C'

    return render(request, 'weather/find_location.html', {
        'weather': weather,
        'city_display': city_display,
        'searched': searched,
        'error_message': error_message,
        'unit_symbol': unit_symbol,
        'preference': pref,
        'find_lat': find_lat,
        'find_lng': find_lng,
    })


@login_required
def map_view(request):
    """
    Render the map page, passing default city/country for initial centering.
    """
    pref, _ = Preference.objects.get_or_create(user=request.user)
    return render(request, 'weather/map.html', {
        'default_city': pref.default_city,
        'default_country': pref.default_country,
    })


@login_required
def map_weather_data(request):
    """
    AJAX endpoint: returns 7-day daily forecast for given lat/lng.
    """
    lat = request.GET.get('lat')
    lon = request.GET.get('lng')
    if not lat or not lon:
        return JsonResponse({'error': 'Missing coordinates.'})

    pref, _ = Preference.objects.get_or_create(user=request.user)
    try:
        cards, city, country, _, _ = WeatherService.by_coords(
            float(lat),
            float(lon),
            days=7,
            units=pref.default_unit
        )
        forecast = [c.__dict__ for c in cards]
        unit = '°F' if pref.default_unit == 'imperial' else '°C'
        return JsonResponse({
            'forecast': forecast,
            'location': city,
            'country': country,
            'unit': unit,
        })
    except WeatherAPIError as e:
        return JsonResponse({'error': str(e)})


@login_required
def map_hourly_data(request):
    """
    AJAX endpoint: returns the next 24 hours of temperature in 3‑h steps
    by using the free /forecast endpoint.
    """
    lat = request.GET.get('lat')
    lon = request.GET.get('lng')
    if not lat or not lon:
        return JsonResponse({'error': 'Missing coordinates.'})

    pref, _ = Preference.objects.get_or_create(user=request.user)
    units = pref.default_unit
    # Free 5‑day /forecast endpoint:
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}"
        f"&units={units}"
        f"&appid={settings.OPENWEATHER_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        # Check for error code
        if data.get('cod') != '200':
            return JsonResponse({'error': data.get('message', 'Error fetching forecast')})

        # Take first 8 entries (8 × 3 h = 24 h)
        hourly_data = [
            {'dt': entry['dt'], 'temp': round(entry['main']['temp'])}
            for entry in data['list'][:8]
        ]
        unit = '°F' if units == 'imperial' else '°C'
        return JsonResponse({'hourly': hourly_data, 'unit': unit})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@login_required
def add_favorite(request):
    """
    Add a city to the user's favorites.
    """
    if request.method == 'POST':
        city    = request.POST.get('city', '').strip()
        country = request.POST.get('country', '').strip().upper()
        if city:
            fav, created = FavoriteLocation.objects.get_or_create(
                user=request.user,
                city_name=city,
                country_code=country,
            )
            msg = f"{city} added!" if created else f"{city} was already saved."
            messages.info(request, msg)
    return redirect('favorites')


@login_required
def remove_favorite(request, favorite_id):
    """
    Remove a favorite location.
    """
    try:
        fav = FavoriteLocation.objects.get(id=favorite_id, user=request.user)
        fav.delete()
        messages.success(request, "Favorite removed.")
    except FavoriteLocation.DoesNotExist:
        messages.error(request, "Favorite not found.")
    return redirect('favorites')


@login_required
def favorites(request):
    """
    Show favorites with today's and tomorrow's weather.
    """
    pref, _ = Preference.objects.get_or_create(user=request.user)
    unit_symbol = '°F' if pref.default_unit == 'imperial' else '°C'

    favorite_weather = []
    for fav in FavoriteLocation.objects.filter(user=request.user):
        try:
            cards, *rest = WeatherService.by_city(
                fav.city_name,
                fav.country_code or None,
                days=2,
                units=pref.default_unit
            )
            today    = cards[0]
            tomorrow = cards[1] if len(cards) > 1 else cards[0]
        except WeatherAPIError as e:
            today = tomorrow = {'error': str(e)}

        favorite_weather.append({
            'id': fav.id,
            'city': fav.city_name,
            'country': fav.country_code,
            'today': today,
            'tomorrow': tomorrow,
        })

    return render(request, 'weather/favorites.html', {
        'favorite_weather': favorite_weather,
        'unit_symbol': unit_symbol,
    })


def about(request):
    return render(request, 'weather/about.html')


def contact(request):
    return render(request, 'weather/contact.html')


def login_view(request):
    """
    Custom login: on POST attempt authenticate; on success redirect home.
    """
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('home')
        return render(request, 'weather/login.html', {'error': 'Invalid credentials'})
    return render(request, 'weather/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile(request):
    """User profile page."""
    return render(request, 'weather/profile.html')
