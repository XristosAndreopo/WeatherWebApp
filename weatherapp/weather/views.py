from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from .models import FavoriteLocation, Preference
from .services import WeatherService, WeatherAPIError

def home(request):
    return render(request, 'weather/home.html')

@login_required
def settings_view(request):
    """
    GET: show the settings form with current preferences.
    POST: save default_city, default_country, default_unit, AND default_theme,
          set a 'theme' cookie so it takes effect immediately, then redirect.
    """
    pref, _ = Preference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update all four preferences from the same form
        pref.default_city    = request.POST.get('default_city', '').strip()
        pref.default_country = request.POST.get('default_country', '').strip().upper()
        pref.default_unit    = request.POST.get('default_unit', 'metric')
        pref.default_theme   = request.POST.get('default_theme', 'light')
        pref.save()

        messages.success(request, 'Preferences saved.')

        # Redirect **and** set the 'theme' cookie to the new value
        response = redirect('settings')
        response.set_cookie('theme', pref.default_theme, max_age=365*24*3600)
        return response

    # On GET, just render the form
    return render(request, 'weather/settings.html', {
        'preference': pref
    })

@login_required
def find_location(request):
    """
    Lookup by ?city=&country= or fall back to default_city/default_country.
    Always pass unit_symbol for templates.
    """
    pref, _ = Preference.objects.get_or_create(user=request.user)

    city_q    = request.GET.get('city', '').strip()
    country_q = request.GET.get('country', '').strip().upper()
    searched  = bool(city_q or pref.default_city)

    if city_q:
        city, country = city_q, (country_q or None)
    else:
        city, country = pref.default_city, (pref.default_country or None)

    weather = city_display = error_message = None
    if searched and city:
        try:
            cards, city_display, _ = WeatherService.by_city(
                city, country,
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
    })

@login_required
def map_view(request):
    """
    Pass default_city & default_country so the JS can center the map there.
    """
    pref, _ = Preference.objects.get_or_create(user=request.user)
    return render(request, 'weather/map.html', {
        'default_city': pref.default_city,
        'default_country': pref.default_country,
    })

@login_required
def map_weather_data(request):
    """
    AJAX: return forecast + unit symbol, location, country.
    """
    lat = request.GET.get('lat')
    lon = request.GET.get('lng')
    if not (lat and lon):
        return JsonResponse({'error': 'Missing coordinates.'})

    pref, _ = Preference.objects.get_or_create(user=request.user)
    try:
        cards, city, country = WeatherService.by_coords(
            float(lat), float(lon),
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
def add_favorite(request):
    if request.method == 'POST':
        city    = request.POST.get('city', '').strip()
        country = request.POST.get('country', '').strip().upper()
        if city:
            fav, created = FavoriteLocation.objects.get_or_create(
                user=request.user,
                city_name=city,
                country_code=country,
            )
            msg = f"{city} added to favorites!" if created else f"{city} already a favorite."
            messages.info(request, msg)
    return redirect('favorites')

@login_required
def favorites(request):
    """
    Show favorites with today/tomorrow cards + unit symbol.
    """
    pref, _ = Preference.objects.get_or_create(user=request.user)
    unit_symbol = '°F' if pref.default_unit == 'imperial' else '°C'

    favorite_weather = []
    for fav in FavoriteLocation.objects.filter(user=request.user):
        try:
            cards, _, _ = WeatherService.by_city(
                fav.city_name, fav.country_code or None,
                days=2,
                units=pref.default_unit
            )
            today, tomorrow = cards[0], cards[1] if len(cards) > 1 else cards[0]
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

@login_required
def remove_favorite(request, favorite_id):
    try:
        fav = FavoriteLocation.objects.get(id=favorite_id, user=request.user)
        fav.delete()
        messages.success(request, "Favorite removed.")
    except FavoriteLocation.DoesNotExist:
        messages.error(request, "Favorite not found.")
    return redirect('favorites')

def about(request):
    return render(request, 'weather/about.html')

def contact(request):
    return render(request, 'weather/contact.html')

def login_view(request):
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
    return render(request, 'weather/profile.html')
