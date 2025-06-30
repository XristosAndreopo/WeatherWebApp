# weatherapp/weather/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from .models import FavoriteLocation, Preference
from .services import WeatherService, WeatherAPIError

def home(request):
    """
    Dashboard / home page.
    """
    return render(request, 'weather/home.html')

@login_required
def settings_view(request):
    """
    User settings page: lets users set their default city, country, and units.
    On GET: displays the form populated with current preferences.
    On POST: saves submitted preferences and redirects back with a success message.
    """
    # Retrieve (or create) the Preference instance for this user
    pref, _ = Preference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update preferences from form data
        pref.default_city = request.POST.get('default_city', '').strip()
        pref.default_country = request.POST.get('default_country', '').strip().upper()
        pref.default_unit = request.POST.get('default_unit', 'metric')
        pref.save()
        messages.success(request, 'Your preferences have been saved.')
        return redirect('settings')

    # Render form with existing preference values
    return render(request, 'weather/settings.html', {
        'preference': pref
    })

@login_required
def find_location(request):
    """
    Handles weather lookup by city/country.
    - If the user provides ?city=… in GET, use that.
    - Otherwise, fall back to their saved default_city (if any).
    Always uses the user's default_unit for temperature.
    """
    pref, _ = Preference.objects.get_or_create(user=request.user)

    # Determine search parameters
    city_q = request.GET.get('city', '').strip()
    country_q = request.GET.get('country', '').strip().upper()
    searched = False

    if city_q:
        # User explicitly searched
        city = city_q
        country = country_q or None
        searched = True
    elif pref.default_city:
        # Fallback to saved preference
        city = pref.default_city
        country = pref.default_country or None
        searched = True
    else:
        # No search yet
        city = country = None

    weather = None
    city_display = None
    error_message = None

    if searched and city:
        try:
            # Fetch up to 7 days of forecast, in user's preferred units
            cards, city_display, _ = WeatherService.by_city(
                city, country,
                days=7,
                units=pref.default_unit
            )
            weather = cards
        except WeatherAPIError as e:
            error_message = str(e)

    return render(request, 'weather/find_location.html', {
        'weather': weather,
        'city_display': city_display,
        'searched': searched,
        'error_message': error_message,
        'preference': pref,  # so template can show units or defaults
    })

@login_required
def map_view(request):
    """
    Map page: displays interactive map and lets user click or search
    to fetch weather via AJAX.
    """
    return render(request, 'weather/map.html')

@login_required
def map_weather_data(request):
    """
    AJAX endpoint: given lat & lng, returns JSON with forecast,
    location name, and country code. Uses user's preferred units.
    """
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    if not lat or not lng:
        return JsonResponse({'error': 'Missing coordinates.'})

    # Get user's unit preference
    pref, _ = Preference.objects.get_or_create(user=request.user)

    try:
        cards, city_name, country_code = WeatherService.by_coords(
            float(lat), float(lng),
            days=7,
            units=pref.default_unit
        )
        # Serialize dataclass instances to dicts
        forecast = [card.__dict__ for card in cards]
        return JsonResponse({
            'forecast': forecast,
            'location': city_name,
            'country': country_code,
        })
    except WeatherAPIError as e:
        return JsonResponse({'error': str(e)})

@login_required
def add_favorite(request):
    """
    POST handler to add the given city/country to the user's favorites.
    Redirects to the favorites page, showing a message.
    """
    if request.method == 'POST':
        city = request.POST.get('city', '').strip()
        country = request.POST.get('country', '').strip().upper()
        if city:
            fav, created = FavoriteLocation.objects.get_or_create(
                user=request.user,
                city_name=city,
                country_code=country,
            )
            if created:
                messages.success(request, f"{city} added to your favorites!")
            else:
                messages.info(request, f"{city} is already in your favorites.")
    return redirect('favorites')

@login_required
def favorites(request):
    """
    Displays the user's favorite locations alongside today's and tomorrow's forecast.
    Uses the user's default_unit preference.
    """
    pref, _ = Preference.objects.get_or_create(user=request.user)

    favorites_qs = FavoriteLocation.objects.filter(user=request.user)
    favorite_weather = []

    for fav in favorites_qs:
        try:
            # Fetch 2-day forecast for each favorite
            cards, _, _ = WeatherService.by_city(
                fav.city_name,
                fav.country_code or None,
                days=2,
                units=pref.default_unit
            )
            today_card = cards[0]
            tomorrow_card = cards[1] if len(cards) > 1 else cards[0]
        except WeatherAPIError as e:
            today_card = tomorrow_card = {'error': str(e)}

        favorite_weather.append({
            'id': fav.id,
            'city': fav.city_name,
            'country': fav.country_code,
            'today': today_card,
            'tomorrow': tomorrow_card,
        })

    return render(request, 'weather/favorites.html', {
        'favorite_weather': favorite_weather
    })

@login_required
def remove_favorite(request, favorite_id):
    """
    Removes the FavoriteLocation with the given ID (if it belongs to the user).
    """
    try:
        fav = FavoriteLocation.objects.get(id=favorite_id, user=request.user)
        fav.delete()
        messages.success(request, "Favorite removed.")
    except FavoriteLocation.DoesNotExist:
        messages.error(request, "Favorite not found.")
    return redirect('favorites')

def about(request):
    """
    Static about page.
    """
    return render(request, 'weather/about.html')

def contact(request):
    """
    Static contact page.
    """
    return render(request, 'weather/contact.html')

def login_view(request):
    """
    Handles user login. On POST, authenticates and redirects to home.
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
        else:
            return render(request, 'weather/login.html', {'error': 'Invalid credentials'})
    return render(request, 'weather/login.html')

def logout_view(request):
    """
    Logs out the current user and redirects to home.
    """
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    """
    User profile page (read‑only for now).
    """
    return render(request, 'weather/profile.html')
