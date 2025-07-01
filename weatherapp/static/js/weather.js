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
// 3) Interactive map + daily & hourly toggle on Map page
// —————————————————————————————————————————
function initWeatherMap() {
  if (typeof L === 'undefined' || !document.getElementById('map')) return;

  // DOM refs
  const cityInput            = document.getElementById('cityInput');
  const countryInput         = document.getElementById('countryInput');
  const searchBtn            = document.getElementById('searchBtn');
  const resultEl             = document.getElementById('weatherResult');
  const favForm              = document.getElementById('mapAddFavForm');
  const favCityField         = document.getElementById('mapAddFavCity');
  const favCountryField      = document.getElementById('mapAddFavCountry');
  const controlsWrapper      = document.getElementById('mapForecastControls');
  const controlsBtn          = document.getElementById('mapForecastDropdown');
  const controlsItems        = controlsWrapper.querySelectorAll('.dropdown-item');
  const dailyContainer       = document.getElementById('weatherResult');
  const hourlyContainer      = document.getElementById('hourlyMapChartContainer');
  const canvasHourlyMap      = document.getElementById('hourlyMapChart');
  const ctxHourlyMap         = canvasHourlyMap?.getContext('2d');
  let hourlyMapChartInstance;
  let lastLat, lastLng;

  // Initialize Leaflet map
  const map = L.map('map').setView([51.505, -0.09], 4);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18
  }).addTo(map);
  const marker = L.marker([51.505, -0.09], { draggable: true }).addTo(map);

  // Build daily forecast cards
  function renderDaily(data) {
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
                <img src="${STATIC_URL}img/weather_icons/${day.icon}" width="48" height="48"><br>
                ${day.description.charAt(0).toUpperCase() + day.description.slice(1)}<br>
                Temp: ${day.temp}${data.unit}<br>
                Humidity: ${day.humidity}%
              </div>
            </div>
          </div>`;
      }
    });
    html += `</div>`;
    resultEl.innerHTML = html;
  }

  // Render hourly Chart.js line chart
  function renderHourly(hourly, unit) {
    if (!ctxHourlyMap) return;
    const labels = hourly.map(h => {
      const d = new Date(h.dt * 1000);
      return d.getHours().toString().padStart(2, '0') + ':00';
    });
    const temps = hourly.map(h => h.temp);
    if (hourlyMapChartInstance) hourlyMapChartInstance.destroy();
    hourlyMapChartInstance = new Chart(ctxHourlyMap, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: `Temp (${unit})`,
          data: temps,
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

  // Fetch hourly data (next 24h)
  function fetchHourly(lat, lng) {
    fetch(`${MAP_HOURLY_URL}?lat=${lat}&lng=${lng}`, {
      credentials: 'same-origin'
    })
    .then(res => res.json())
    .then(data => {
      if (data.hourly) renderHourly(data.hourly, data.unit);
    })
    .catch(console.error);
  }

  // Fetch daily forecast (then show toggle and optionally preload hourly)
  function fetchMapWeather(lat, lng) {
    lastLat = lat; lastLng = lng;
    fetch(`${MAP_WEATHER_URL}?lat=${lat}&lng=${lng}`, {
      credentials: 'same-origin'
    })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        resultEl.innerHTML = `<div class="alert alert-warning">${data.error}</div>`;
        controlsWrapper.style.display = 'none';
        return;
      }
      renderDaily(data);

      // Show favorites form if logged in
      if (favForm && data.location && !data.forecast[0].error) {
        favCityField.value    = data.location;
        favCountryField.value = data.country;
        favForm.style.display  = 'block';
      }

      // Show toggle controls, reset to daily view
      controlsWrapper.style.display = '';
      controlsBtn.textContent = 'Show: Daily';
      dailyContainer.style.display  = '';
      hourlyContainer.style.display = 'none';

      // Preload hourly data (chart renders when “Next 24 Hrs” chosen)
      fetchHourly(lat, lng);
    })
    .catch(() => {
      resultEl.innerHTML = `<div class="alert alert-danger">Error fetching weather data.</div>`;
      controlsWrapper.style.display = 'none';
    });
  }

  // Wire up dropdown toggle
  controlsItems.forEach(item => {
    item.addEventListener('click', e => {
      e.preventDefault();
      const choice = item.dataset.forecast; // "daily" or "hourly"
      controlsBtn.textContent = `Show: ${item.textContent}`;

      if (choice === 'daily') {
        dailyContainer.style.display  = '';
        hourlyContainer.style.display = 'none';
      } else {
        dailyContainer.style.display  = 'none';
        hourlyContainer.style.display = '';
        if (lastLat != null && lastLng != null) {
          fetchHourly(lastLat, lastLng);
        }
      }
    });
  });

  // Map click & marker drag
  map.on('click', e => {
    fetchMapWeather(e.latlng.lat, e.latlng.lng);
    marker.setLatLng(e.latlng);
  });
  marker.on('dragend', () => {
    const { lat, lng } = marker.getLatLng();
    fetchMapWeather(lat, lng);
  });

  // Geolocation on load
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      const { latitude, longitude } = pos.coords;
      map.setView([latitude, longitude], 8);
      marker.setLatLng([latitude, longitude]);
      fetchMapWeather(latitude, longitude);
    });
  }

  // Search button handler
  searchBtn.addEventListener('click', e => {
    e.preventDefault();
    const city    = cityInput.value.trim();
    const country = countryInput.value.trim();
    if (!city) return;
    let q = city;
    if (country) q += `,${country}`;
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .then(loc => {
        if (!loc.length) return alert('Location not found.');
        const { lat, lon } = loc[0];
        map.setView([+lat, +lon], 8);
        marker.setLatLng([+lat, +lon]);
        fetchMapWeather(+lat, +lon);
      });
  });

  // Center map on default preferences
  if (DEFAULT_CITY) {
    let q = DEFAULT_CITY;
    if (DEFAULT_COUNTRY) q += `,${DEFAULT_COUNTRY}`;
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .then(loc => {
        if (!loc.length) return;
        const { lat, lon } = loc[0];
        map.setView([+lat, +lon], 8);
        marker.setLatLng([+lat, +lon]);
        fetchMapWeather(+lat, +lon);
      });
  }
}

// —————————————————————————————
// 4) Dropdown‑style toggle for Find‑by‑Location
// —————————————————————————————
function initFindDropdown() {
  console.log("📊 initFindDropdown running");
  const container = document.getElementById('findSection');
  if (!container) return;

  const dropdownBtn = container.querySelector('#forecastDropdown');
  const items       = container.querySelectorAll('.dropdown-item');
  const dailyDiv    = document.getElementById('dailyForecast');
  const hourlyDiv   = document.getElementById('hourlyForecast');
  const ctx         = document.getElementById('findHourlyChart')?.getContext('2d');
  let chartInst;

  // extract coords once
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

  // initialize on daily view
  const dailyInit = document.getElementById('dailyForecast');
  const hourlyInit = document.getElementById('hourlyForecast');
  if (dailyInit && hourlyInit) {
    dailyInit.style.display  = '';
    hourlyInit.style.display = 'none';
  }
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
