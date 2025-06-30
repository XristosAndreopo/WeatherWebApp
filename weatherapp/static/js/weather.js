// weatherapp/static/js/weather.js

// ———————————————————————————————————————
// Dashboard: Random weather quotes
// ———————————————————————————————————————
const WEATHER_QUOTES = [
  "Wherever you go, no matter what the weather, always bring your own sunshine.",
  // … (rest of your quotes) …
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
// Forecast slider on “Find by Location”
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
// Interactive map on “Map” page
// ———————————————————————————————————————
function initWeatherMap() {
  if (typeof L === 'undefined' || !document.getElementById('map')) return;

  // DOM references
  const cityInput     = document.getElementById('cityInput');
  const countryInput  = document.getElementById('countryInput');
  const searchBtn     = document.getElementById('searchBtn');
  const resultEl      = document.getElementById('weatherResult');
  const favForm       = document.getElementById('mapAddFavForm');
  const favCityField  = document.getElementById('mapAddFavCity');
  const favCountryField = document.getElementById('mapAddFavCountry');

  // Initialize Leaflet
  const map = L.map('map').setView([51.505, -0.09], 4);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18
  }).addTo(map);

  const marker = L.marker([51.505, -0.09], { draggable: true }).addTo(map);

  // Fetch & render weather forecast
  function fetchWeather(lat, lng) {
    fetch(`${MAP_WEATHER_URL}?lat=${lat}&lng=${lng}`, {
      credentials: 'same-origin'
    })
      .then(res => res.json())
      .then(data => {
        // Render forecast cards
        if (data.error) {
          resultEl.innerHTML = `<div class="alert alert-warning">${data.error}</div>`;
          if (favForm) favForm.style.display = 'none';
          return;
        }

        let html = `<h4>Forecast for ${data.location}</h4><div class="row">`;
        data.forecast.forEach(day => {
          if (day.error) {
            html += `
              <div class="col-md-3 mb-3">
                <div class="card text-center">
                  <div class="card-body text-danger">${day.error}</div>
                </div>
              </div>`;
          } else {
            html += `
              <div class="col-md-3 mb-3">
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

        // Show & populate “Add to Favorites”
        if (favForm) {
          favCityField.value    = data.location;
          favCountryField.value = data.country;
          favForm.style.display  = 'block';
        }
      })
      .catch(() => {
        resultEl.innerHTML = '<div class="alert alert-danger">Error fetching weather data.</div>';
        if (favForm) favForm.style.display = 'none';
      });
  }

  // Map click & marker drag
  map.on('click', e => {
    marker.setLatLng(e.latlng);
    fetchWeather(e.latlng.lat, e.latlng.lng);
  });
  marker.on('dragend', () => {
    const { lat, lng } = marker.getLatLng();
    fetchWeather(lat, lng);
  });

  // Geolocation on load
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      const { latitude, longitude } = pos.coords;
      map.setView([latitude, longitude], 8);
      marker.setLatLng([latitude, longitude]);
      fetchWeather(latitude, longitude);
    });
  }

  // Search button click
  searchBtn.addEventListener('click', e => {
    e.preventDefault();
    const city    = cityInput.value.trim();
    const country = countryInput.value.trim();
    if (!city) return;

    let q = city;
    if (country) q += `,${country}`;

    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}`)
      .then(res => res.json())
      .then(locations => {
        if (!locations.length) {
          alert('Location not found.');
          return;
        }
        const { lat, lon } = locations[0];
        const fLat = parseFloat(lat), fLon = parseFloat(lon);
        map.setView([fLat, fLon], 8);
        marker.setLatLng([fLat, fLon]);
        fetchWeather(fLat, fLon);
      });
  });
}

// ———————————————————————————————————————
// Bootstrap all initializers on DOM ready
// ———————————————————————————————————————
document.addEventListener('DOMContentLoaded', () => {
  initDashboardQuotes();
  initForecastSlider();
  initWeatherMap();
});
