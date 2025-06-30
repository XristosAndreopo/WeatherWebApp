// weatherapp/static/js/weather.js

// ———————————————————————————————————————
// 1) Dashboard: Random weather quotes
// ———————————————————————————————————————
const WEATHER_QUOTES = [
    "Wherever you go, no matter what the weather, always bring your own sunshine.",
    "A change in the weather is sufficient to recreate the world and ourselves.",
    "Sunshine is delicious, rain is refreshing, wind braces us up, snow is exhilarating.",
    "After rain comes the rainbow.",
    "There’s no such thing as bad weather, just soft people.",
    "The sound of rain needs no translation.",
    "Clouds come floating into my life, no longer to carry rain or usher storm, but to add color to my sunset sky.",
    "If you want to see the sunshine, you have to weather the storm.",
    "The best thing one can do when it's raining is to let it rain.",
    "The sky is the daily bread of the eyes.",
    "Let the wind carry away your worries.",
    "Rain is just confetti from the sky."
];

function initDashboardQuotes() {
  const el = document.getElementById('weatherQuote');
  if (!el) return;
  el.textContent = WEATHER_QUOTES[
    Math.floor(Math.random() * WEATHER_QUOTES.length)
  ];
}

// ———————————————————————————————————————
// 2) Forecast slider on “Find by Location”
// ———————————————————————————————————————
function initForecastSlider() {
  const slider = document.getElementById('daySlider');
  const label  = document.getElementById('sliderValue');
  const cards  = Array.from(document.querySelectorAll('.forecast-day'));
  if (!slider || !label || cards.length === 0) return;

  const update = () => {
    const n = parseInt(slider.value, 10);
    label.textContent = n;
    cards.forEach((card, i) => {
      card.style.display = i < n ? '' : 'none';
    });
  };

  slider.addEventListener('input', update);
  update();
}

// ———————————————————————————————————————
// 3) Interactive map on “Map” page
// ———————————————————————————————————————
function initWeatherMap() {
  const mapContainer = document.getElementById('map');
  if (!mapContainer || typeof L === 'undefined') return;

  const map = L.map('map').setView([51.505, -0.09], 4);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18
  }).addTo(map);

  const marker = L.marker([51.505, -0.09], { draggable: true }).addTo(map);

  const fetchWeather = (lat, lng) => {
    fetch(`${MAP_WEATHER_URL}?lat=${lat}&lng=${lng}`, { credentials: 'same-origin' })
      .then(r => r.json())
      .then(data => {
        const resultEl = document.getElementById('weatherResult');
        const favEl    = document.getElementById('addFavoriteBtn');
        if (data.error) {
          resultEl.innerHTML = `<div class="alert alert-warning">${data.error}</div>`;
          favEl.innerHTML    = '';
          return;
        }
        let html = `<h4>Forecast for ${data.location}</h4><div class="row">`;
        data.forecast.forEach(day => {
          if (day.error) {
            html += `<div class="col-md-3 mb-3"><div class="card text-center">
                       <div class="card-body text-danger">${day.error}</div>
                     </div></div>`;
          } else {
            html += `<div class="col-md-3 mb-3">
                       <div class="card text-center">
                         <div class="card-body">
                           <strong>${day.date}</strong><br>
                           <img src="${STATIC_URL}img/weather_icons/${day.icon}"
                                width="48" height="48" alt=""><br>
                           ${day.description.charAt(0).toUpperCase() + day.description.slice(1)}<br>
                           Temp: ${day.temp}&deg;C<br>
                           Humidity: ${day.humidity}%
                         </div>
                       </div>
                     </div>`;
          }
        });
        html += `</div>`;
        resultEl.innerHTML = html;

        if (IS_AUTHENTICATED && data.location && !data.forecast[0].error) {
          favEl.innerHTML = `
            <form method="post" action="${ADD_FAV_URL}">
              <input type="hidden" name="csrfmiddlewaretoken" value="${CSRF_TOKEN}">
              <input type="hidden" name="city"    value="${data.location}">
              <input type="hidden" name="country" value="${data.country}">
              <button type="submit" class="btn btn-outline-success mt-3">
                Add to Favorites
              </button>
            </form>`;
        } else {
          favEl.innerHTML = '';
        }
      })
      .catch(() => {
        document.getElementById('weatherResult')
          .innerHTML = '<div class="alert alert-danger">Error fetching weather data.</div>';
        document.getElementById('addFavoriteBtn').innerHTML = '';
      });
  };

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      const { latitude: lat, longitude: lng } = pos.coords;
      map.setView([lat, lng], 8);
      marker.setLatLng([lat, lng]);
      fetchWeather(lat, lng);
    });
  }

  map.on('click', e => {
    marker.setLatLng(e.latlng);
    fetchWeather(e.latlng.lat, e.latlng.lng);
  });
  marker.on('dragend', () => {
    const { lat, lng } = marker.getLatLng();
    fetchWeather(lat, lng);
  });

  document.getElementById('searchBtn')?.addEventListener('click', () => {
    const q = document.getElementById('locationSearch').value.trim();
    if (!q) return;
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .then(locations => {
        if (locations.length) {
          const { lat, lon } = locations[0];
          const fl = parseFloat(lat), fn = parseFloat(lon);
          map.setView([fl, fn], 8);
          marker.setLatLng([fl, fn]);
          fetchWeather(fl, fn);
        } else {
          alert("Location not found.");
        }
      });
  });
}

// ———————————————————————————————————————
// 4) Initialize everything on DOM ready
// ———————————————————————————————————————
document.addEventListener('DOMContentLoaded', () => {
  initDashboardQuotes();
  initForecastSlider();
  initWeatherMap();
});
