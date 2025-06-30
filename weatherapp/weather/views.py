# weather/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .services import WeatherService, WeatherAPIError
from .models import FavoriteLocation

def home(request):
    return render(request, 'weather/home.html')

def settings_view(request):
    return render(request, 'weather/settings.html')

@login_required
def find_location(request):
    context = {'searched': False}
    city = request.GET.get('city', '').strip()
    if city:
        context['searched'] = True
        country = request.GET.get('country', '').strip().upper() or None
        try:
            cards, city_name, _ = WeatherService.by_city(city, country)
            context.update({
                'weather': cards,
                'city_display': city_name,
            })
        except WeatherAPIError as e:
            context['error_message'] = str(e)
    return render(request, 'weather/find_location.html', context)

@login_required
def map_view(request):
    return render(request, 'weather/map.html')

@login_required
def map_weather_data(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lng')
    if not lat or not lon:
        return JsonResponse({'error': 'Missing coordinates.'})
    try:
        cards, city, country = WeatherService.by_coords(float(lat), float(lon))
        # Serialize ForecastCard dataclass to dict
        forecast = [c.__dict__ for c in cards]
        return JsonResponse({
            'forecast': forecast,
            'location': city,
            'country': country,
        })
    except WeatherAPIError as e:
        return JsonResponse({'error': str(e)})

@login_required
def add_favorite(request):
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
    favs = FavoriteLocation.objects.filter(user=request.user)
    favorite_weather = []
    for f in favs:
        try:
            cards, _, _ = WeatherService.by_city(f.city_name, f.country_code, days=2)
            today_card, tomorrow_card = cards[0], cards[1] if len(cards) > 1 else cards[0]
        except WeatherAPIError as e:
            today_card = tomorrow_card = {'error': str(e)}
        favorite_weather.append({
            'id': f.id,
            'city': f.city_name,
            'country': f.country_code,
            'today': today_card,
            'tomorrow': tomorrow_card,
        })
    return render(request, 'weather/favorites.html', {'favorite_weather': favorite_weather})

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
        from django.contrib.auth import authenticate, login
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
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    return render(request, 'weather/profile.html')
