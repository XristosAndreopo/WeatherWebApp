from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import requests
from datetime import datetime, timedelta
from .models import FavoriteLocation
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Weather icon mapping helper - define ONCE and use everywhere
def get_icon_for_description(description):
    description = description.lower()
    if 'clear' in description:
        return 'clear.png'
    elif 'few clouds' in description:
        return 'few_clouds.png'
    elif 'scattered clouds' in description:
        return 'scattered_clouds.png'
    elif 'broken clouds' in description:
        return 'broken_clouds.png'
    elif 'shower rain' in description:
        return 'shower_rain.png'
    elif 'rain' in description:
        return 'rain.png'
    elif 'thunderstorm' in description:
        return 'thunderstorm.png'
    elif 'snow' in description:
        return 'snow.png'
    elif 'mist' in description:
        return 'mist.png'
    else:
        return 'default.png'

def home(request):
    """Dashboard/home page."""
    return render(request, 'weather/home.html')

def settings(request):
    """User settings page."""
    return render(request, 'weather/settings.html')

@login_required
def find_location(request):
    """
    Handles weather search by city/country.
    Fetches 5-day forecast from OpenWeatherMap and passes it to the template.
    Always puts today's forecast (or error card) as the first card.
    """
    weather = None
    city_display = None
    searched = False
    error_message = None

    api_key = "11742b368f7333908e02de4245144cb1"
    if request.method == 'GET' and ('city' in request.GET):
        city = request.GET.get('city', '').strip()
        country = request.GET.get('country', '').strip().upper()
        searched = True

        if not api_key or api_key.strip() == '':
            weather = None
            error_message = 'API key missing'
        else:
            if country:
                location = f"{city},{country}"
            else:
                location = city
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&units=metric&appid={api_key}"

            try:
                response = requests.get(url)
                data = response.json()

                if data.get('cod') != '200':
                    weather = None
                    error_message = data.get('message', 'Error fetching data')
                else:
                    now = datetime.utcnow()
                    forecasts = data['list']
                    days = {}
                    last_forecast = {}
                    today_str = now.strftime('%Y-%m-%d')
                    today_card = None
                    last_today_card = None
                    for f in forecasts:
                        dt = datetime.fromtimestamp(f['dt'])
                        date_str = dt.strftime('%Y-%m-%d')
                        description = f['weather'][0]['description']
                        card = {
                            'date': dt.strftime('%Y-%m-%d %H:%M'),
                            'description': description,
                            'temp': round(f['main']['temp']),
                            'humidity': f['main']['humidity'],
                            'icon': get_icon_for_description(description),
                        }
                        last_forecast[date_str] = card  # always keep latest for each day
                        if date_str not in days:
                            if dt >= now or not days.get(date_str):
                                days[date_str] = card
                        # Track today's card
                        if date_str == today_str:
                            if dt >= now and not today_card:
                                today_card = card
                            last_today_card = card
                    # Guarantee today is first in the weather list
                    weather = []
                    if today_str in days:
                        weather.append(days[today_str])
                        del days[today_str]
                    elif last_today_card:
                        weather.append(last_today_card)
                        days.pop(today_str, None)
                    else:
                        weather.append({'error': 'No forecast data for today.'})
                    # Now add the rest (sorted by date)
                    for k in sorted(days.keys()):
                        weather.append(days[k])
                    weather = weather[:7]
                    city_display = data['city']['name']
            except Exception as e:
                weather = None
                error_message = str(e)

    context = {
        'weather': weather,
        'city_display': city_display,
        'searched': searched,
        'error_message': error_message,
    }
    return render(request, 'weather/find_location.html', context)

@login_required
def map_view(request):
    """Show weather map."""
    return render(request, 'weather/map.html')

def about(request):
    """About page."""
    return render(request, 'weather/about.html')

def contact(request):
    """Contact page."""
    return render(request, 'weather/contact.html')

@login_required
def profile(request):
    """User profile page."""
    return render(request, 'weather/profile.html')

def login_view(request):
    """Custom login view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'weather/login.html', {'error': 'Invalid credentials'})
    return render(request, 'weather/login.html')

def logout_view(request):
    """Logout view."""
    logout(request)
    return redirect('home')

@login_required
@csrf_exempt
def add_favorite(request):
    """
    Add a city/country as favorite for the logged-in user.
    """
    if request.method == 'POST':
        city = request.POST.get('city', '').strip()
        country = request.POST.get('country', '').strip().upper()
        if city:
            # Prevent duplicates
            favorite, created = FavoriteLocation.objects.get_or_create(
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
    Show user's favorite locations with today's and tomorrow's weather for each.
    Always includes today's nearest available forecast (or last available if all are past).
    If there is no valid forecast for today, return an error card for today.
    """
    api_key = "11742b368f7333908e02de4245144cb1"
    favorites = FavoriteLocation.objects.filter(user=request.user)
    favorite_weather = []

    for fav in favorites:
        city = fav.city_name
        country = fav.country_code
        location = f"{city},{country}" if country else city
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&units=metric&appid={api_key}"

        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        now = datetime.utcnow()
        today_forecast = None
        tomorrow_forecast = None
        last_today = None

        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if data.get('cod') == '200':
                for item in data['list']:
                    dt = datetime.fromtimestamp(item['dt'])
                    date_only = dt.date()
                    desc = item['weather'][0]['description']
                    icon = get_icon_for_description(desc)
                    card = {
                        'date': dt.strftime('%Y-%m-%d %H:%M'),
                        'description': desc,
                        'temp': round(item['main']['temp']),
                        'humidity': item['main']['humidity'],
                        'icon': icon,
                    }
                    if date_only == today:
                        last_today = card  # keep updating; ends up as last for today
                        if dt >= now and not today_forecast:
                            today_forecast = card
                    elif date_only == tomorrow and not tomorrow_forecast:
                        tomorrow_forecast = card
                    if today_forecast and tomorrow_forecast:
                        break
                # If no *future* forecast for today, use the last available
                if not today_forecast and last_today:
                    today_forecast = last_today
                # If still nothing, or any key is missing, set an error card
                if (not today_forecast or
                    'icon' not in today_forecast or
                    'temp' not in today_forecast or
                    'humidity' not in today_forecast):
                    today_forecast = {'error': "No forecast data for today."}
                if not tomorrow_forecast:
                    tomorrow_forecast = {'error': "No forecast data for tomorrow."}
            else:
                today_forecast = {'error': data.get('message', 'No data')}
                tomorrow_forecast = {'error': data.get('message', 'No data')}
        except Exception as e:
            today_forecast = {'error': str(e)}
            tomorrow_forecast = {'error': str(e)}

        favorite_weather.append({
            'city': city,
            'country': country,
            'today': today_forecast,
            'tomorrow': tomorrow_forecast,
            'id': fav.id,
        })

    return render(request, 'weather/favorites.html', {'favorite_weather': favorite_weather})


@login_required
@csrf_exempt
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

# AJAX API for map weather (unchanged except for adding forecast time)
@login_required
def map_weather_data(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    api_key = "11742b368f7333908e02de4245144cb1"

    if not lat or not lng:
        return JsonResponse({'error': 'Missing coordinates.'})

    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lng}&units=metric&appid={api_key}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get('cod') != '200':
            return JsonResponse({'error': data.get('message', 'Weather API error')})

        now = datetime.utcnow()
        forecasts = data['list']
        days = {}
        last_forecast = {}
        today_str = now.strftime('%Y-%m-%d')
        today_card = None
        last_today_card = None
        for f in forecasts:
            dt = datetime.fromtimestamp(f['dt'])
            date_str = dt.strftime('%Y-%m-%d')
            desc = f['weather'][0]['description']
            card = {
                'date': dt.strftime('%Y-%m-%d %H:%M'),
                'description': desc,
                'temp': round(f['main']['temp']),
                'humidity': f['main']['humidity'],
                'icon': get_icon_for_description(desc),
            }
            last_forecast[date_str] = card  # always keep latest for each day
            if date_str not in days:
                if dt >= now or not days.get(date_str):
                    days[date_str] = card
            if date_str == today_str:
                if dt >= now and not today_card:
                    today_card = card
                last_today_card = card
        # Guarantee today is first in the forecast
        forecast = []
        if today_str in days:
            forecast.append(days[today_str])
            del days[today_str]
        elif last_today_card:
            forecast.append(last_today_card)
            days.pop(today_str, None)
        else:
            forecast.append({'error': 'No forecast data for today.'})
        for k in sorted(days.keys()):
            forecast.append(days[k])
        forecast = forecast[:7]

        city_name = data['city']['name']
        country_code = data['city'].get('country', '')

        return JsonResponse({
            'location': city_name,
            'country': country_code,
            'forecast': forecast,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})
