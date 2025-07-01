// weatherapp/static/js/weather.js

// —————————————————————————————————————————
// 1) Dashboard: Random weather quotes
// —————————————————————————————————————————
console.log("✅ weather.js loaded and running");
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

// —————————————————————————————————————————
// 2) Forecast slider on “Find by Location”
// —————————————————————————————————————————
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

// —————————————————————————————————————————
// 3) Interactive map + daily forecast
// —————————————————————————————————————————
function initWeatherMap() {
  if (typeof L === 'undefined' || !document.getElementById('map')) return;

  // DOM refs
  const cityInput        = document.getElementById('cityInput');
  const countryInput     = document.getElementById('countryInput');
  const searchBtn        = document.getElementById('searchBtn');
  const resultEl         = document.getElementById('weatherResult');
  const favForm          = document.getElementById('mapAddFavForm');
  const favCityField     = document.getElementById('mapAddFavCity');
  const favCountryField  = document.getElementById('mapAddFavCountry');
  const canvasHourly     = document.getElementById('hourlyChart');
  const ctxHourly        = canvasHourly?.getContext('2d');
  let hourlyChartInst;

  // Initialize Leaflet
  const map = L.map('map').setView([51.505, -0.09], 4);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18 }).addTo(map);
  const marker = L.marker([51.505, -0.09], { draggable: true }).addTo(map);

  // Render Chart.js line chart (next 24h)
  function renderHourlyChart(hourly, unit) {
    if (!ctxHourly) return;
    const labels = hourly.map(h => {
      const d = new Date(h.dt * 1000);
      return d.getHours().toString().padStart(2, '0') + ':00';
    });
    const data = hourly.map(h => h.temp);
    if (hourlyChartInst) hourlyChartInst.destroy();
    hourlyChartInst = new Chart(ctxHourly, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: `Temperature (${unit})`,
          data,
          fill: false,
          tension: 0.2
        }]
      },
      options: {
        scales: {
          x: { title: { display: true, text: 'Hour' } },
          y: { title: { display: true, text: `Temp (${unit})` } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  // Fetch next 24h hourly data
  function fetchHourly(lat, lng) {
    fetch(`${MAP_HOURLY_URL}?lat=${lat}&lng=${lng}`, { credentials: 'same-origin' })
      .then(r => r.json())
      .then(data => {
        if (data.hourly && Array.isArray(data.hourly)) {
          renderHourlyChart(data.hourly, data.unit);
        }
      })
      .catch(() => {
        // fail silently
      });
  }

  // Fetch daily forecast & then hourly
  function fetchWeather(lat, lng) {
    fetch(`${MAP_WEATHER_URL}?lat=${lat}&lng=${lng}`, { credentials: 'same-origin' })
      .then(r => r.json())
      .then(data => {
        if (data.error) {
          resultEl.innerHTML = `<div class="alert alert-warning">${data.error}</div>`;
          if (favForm) favForm.style.display = 'none';
          return;
        }

        // Build daily cards
        let html = `<h4>Forecast for ${data.location}</h4><div class="row">`;
        data.forecast.forEach(day => {
          html += day.error
            ? `<div class="col-md-3 mb-3">
                 <div class="card text-center"><div class="card-body text-danger">${day.error}</div></div>
               </div>`
            : `<div class="col-md-3 mb-3">
                 <div class="card text-center"><div class="card-body">
                   <strong>${day.date}</strong><br>
                   <img src="${STATIC_URL}img/weather_icons/${day.icon}" width="48" height="48" alt=""><br>
                   ${day.description.charAt(0).toUpperCase() + day.description.slice(1)}<br>
                   Temp: ${day.temp}${data.unit}<br>
                   Humidity: ${day.humidity}%
                 </div></div>
               </div>`;
        });
        html += `</div>`;
        resultEl.innerHTML = html;

        // Show favorites form
        if (favForm && data.location && !data.forecast[0].error) {
          favCityField.value    = data.location;
          favCountryField.value = data.country;
          favForm.style.display  = 'block';
        }

        // Then draw hourly
        fetchHourly(lat, lng);
      })
      .catch(() => {
        resultEl.innerHTML = '<div class="alert alert-danger">Error fetching weather data.</div>';
        if (favForm) favForm.style.display = 'none';
      });
  }

  // Map click & drag
  map.on('click', e => {
    marker.setLatLng(e.latlng);
    fetchWeather(e.latlng.lat, e.latlng.lng);
  });
  marker.on('dragend', () => {
    const { lat, lng } = marker.getLatLng();
    fetchWeather(lat, lng);
  });

  // Geolocation
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      const { latitude, longitude } = pos.coords;
      map.setView([latitude, longitude], 8);
      marker.setLatLng([latitude, longitude]);
      fetchWeather(latitude, longitude);
    });
  }

  // Search box
  searchBtn.addEventListener('click', e => {
    e.preventDefault();
    const city = cityInput.value.trim(), country = countryInput.value.trim();
    if (!city) return;
    const q = city + (country ? `, ${country}` : '');
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .then(loc => {
        if (!loc.length) return alert('Location not found.');
        const { lat, lon } = loc[0], fLat = +lat, fLon = +lon;
        map.setView([fLat, fLon], 8);
        marker.setLatLng([fLat, fLon]);
        fetchWeather(fLat, fLon);
      });
  });

  // Center on default
  if (DEFAULT_CITY) {
    const q = DEFAULT_CITY + (DEFAULT_COUNTRY ? `, ${DEFAULT_COUNTRY}` : '');
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .then(loc => {
        if (!loc.length) return;
        const { lat, lon } = loc[0], fLat = +lat, fLon = +lon;
        map.setView([fLat, fLon], 8);
        marker.setLatLng([fLat, fLon]);
        fetchWeather(fLat, fLon);
      });
  }
}

// —————————————————————————————————————————
// 4) Dropdown‑style toggle for Find‑by‑Location
// —————————————————————————————————————————
function initFindDropdown() {
  console.log("📊 initFindDropdown running");
  const container   = document.getElementById('findSection');
  if (!container) return;

  const dropdownBtn = container.querySelector('#forecastDropdown');
  const items       = container.querySelectorAll('.dropdown-item');
  const dailyDiv    = document.getElementById('dailyForecast');
  const hourlyDiv   = document.getElementById('hourlyForecast');
  const ctx         = document.getElementById('findHourlyChart')?.getContext('2d');
  let chartInst;

  // grab coords once
  const lat = parseFloat(container.dataset.lat);
  const lng = parseFloat(container.dataset.lng);

  items.forEach(item => {
    item.addEventListener('click', e => {
      e.preventDefault();
      const choice = item.dataset.forecast; // "daily" or "hourly"
      dropdownBtn.textContent = `Show: ${item.textContent}`;

      if (choice === 'daily') {
        dailyDiv.style.display  = '';
        hourlyDiv.style.display = 'none';
      } else {
        dailyDiv.style.display  = 'none';
        hourlyDiv.style.display = '';

        if (isNaN(lat) || isNaN(lng) || !ctx) return;

        fetch(`${MAP_HOURLY_URL}?lat=${lat}&lng=${lng}`, {
          credentials: 'same-origin'
        })
          .then(r => r.json())
          .then(data => {
            if (!data.hourly) return;
            const labels = data.hourly.map(h => {
              const d = new Date(h.dt * 1000);
              return d.getHours().toString().padStart(2, '0') + ':00';
            });
            const temps = data.hourly.map(h => h.temp);

            if (chartInst) chartInst.destroy();
            chartInst = new Chart(ctx, {
              type: 'line',
              data: {
                labels,
                datasets: [{
                  label: `Temp (${data.unit})`,
                  data: temps,
                  fill: false,
                  tension: 0.2
                }]
              },
              options: {
                scales: {
                  x: { title: { display: true, text: 'Hour' } },
                  y: { title: { display: true, text: `Temp (${data.unit})` } }
                },
                plugins: { legend: { display: false } }
              }
            });
          })
          .catch(console.error);
      }
    });
  });

  // start on daily view
  dailyDiv.style.display  = '';
  hourlyDiv.style.display = 'none';
}

// —————————————————————————————
// Initialize everything once
// —————————————————————————————
document.addEventListener('DOMContentLoaded', () => {
  initDashboardQuotes();
  initForecastSlider();
  initWeatherMap();
  initFindDropdown();
});
