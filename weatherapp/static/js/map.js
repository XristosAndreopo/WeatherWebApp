// File: static/js/map.js
// ───────────────────────────────────────────────────────────────────────────────
// Module: Interactive Weather Map (self‑initializing)
//
// Responsibilities:
//   1. Initialize a Leaflet map with a draggable marker.
//   2. Geocode user-entered city/country via Nominatim on form submit.
//   3. Fetch & render daily forecast cards via AJAX.
//   4. Fetch & render hourly temperature chart via AJAX.
//   5. Wire up map-click and marker-drag events to reload forecasts.
//   6. Preload a forecast for the form’s default city on page load.
//
// Analytical notes:
//   - We log key steps so you can trace behavior in DevTools.
//   - We always run `initialSearch()` after setup so the map page
//     shows a forecast immediately for your default city.
// ───────────────────────────────────────────────────────────────────────────────

async function initWeatherMap() {
  console.log('⚙️ initWeatherMap running…');

  // 1) Ensure Leaflet & map container exist
  if (typeof L === 'undefined' || !document.getElementById('map')) {
    console.warn('Leaflet or #map container missing; aborting map init.');
    return;
  }

  // 2) Grab DOM elements
  const form            = document.getElementById('mapSearchForm');
  const cityInput       = document.getElementById('cityInput');
  const countryInput    = document.getElementById('countryInput');
  const resultEl        = document.getElementById('weatherResult');
  const favForm         = document.getElementById('mapAddFavForm');
  const favCityField    = document.getElementById('mapAddFavCity');
  const favCountryField = document.getElementById('mapAddFavCountry');
  const controlsWrapper = document.getElementById('mapForecastControls');
  const controlsBtn     = document.getElementById('mapForecastDropdown');
  const controlsItems   = controlsWrapper.querySelectorAll('.dropdown-item');
  const hourlyContainer = document.getElementById('hourlyMapChartContainer');
  const ctxHourly       = document.getElementById('hourlyMapChart')?.getContext('2d');

  console.log('DOM refs initialized:', {
    form, cityInput, countryInput, resultEl, controlsWrapper, controlsBtn
  });

  let hourlyChart = null;
  let lastCoords = { lat: null, lng: null };

  // 3) Initialize Leaflet map & marker
  const map = L.map('map').setView([51.505, -0.09], 4);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18
  }).addTo(map);
  const marker = L.marker([51.505, -0.09], { draggable: true }).addTo(map);

  // 4) Render daily forecast cards
  function renderDaily(data) {
    let html = `<h4>Forecast for ${data.location}</h4><div class="row">`;
    data.forecast.forEach(day => {
      html += `<div class="col-md-3 mb-3"><div class="card text-center"><div class="card-body">`;
      if (day.error) {
        html += `<div class="text-danger">${day.error}</div>`;
      } else {
        html += `
          <strong>${day.date}</strong><br>
          <img src="${window.STATIC_URL}img/weather_icons/${day.icon}" width="48" height="48"><br>
          ${day.description.charAt(0).toUpperCase() + day.description.slice(1)}<br>
          Temp: ${day.temp}${data.unit}<br>
          Humidity: ${day.humidity}%
        `;
      }
      html += `</div></div></div>`;
    });
    html += `</div>`;
    resultEl.innerHTML = html;
  }

  // 5) Fetch & display daily forecast via AJAX
  async function fetchDaily(lat, lng) {
    lastCoords = { lat, lng };
    console.log(`🔄 fetchDaily(${lat}, ${lng})`);
    try {
      const res  = await fetch(
        `${window.MAP_WEATHER_URL}?lat=${lat}&lng=${lng}`, {
          credentials: 'same-origin',
          headers: { 'X-CSRFToken': window.CSRF_TOKEN }
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      renderDaily(data);
      controlsWrapper.style.display = '';
      hourlyContainer.style.display = 'none';

      // Show the “Add to Favorites” form populated
      if (favForm) {
        favCityField.value    = data.location;
        favCountryField.value = data.country;
        favForm.style.display  = 'block';
      }
    } catch (err) {
      console.error('❌ Daily fetch error:', err);
      resultEl.innerHTML = `<div class="alert alert-warning">${err.message}</div>`;
      controlsWrapper.style.display = 'none';
      if (favForm) favForm.style.display = 'none';
    }
  }

  // 6) Fetch & display hourly chart via AJAX
  async function fetchHourly(lat, lng) {
    if (!ctxHourly) return;
    console.log(`🔄 fetchHourly(${lat}, ${lng})`);
    try {
      const res  = await fetch(
        `${window.MAP_HOURLY_URL}?lat=${lat}&lng=${lng}`, {
          credentials: 'same-origin',
          headers: { 'X-CSRFToken': window.CSRF_TOKEN }
      });
      const body = await res.json();
      if (body.error) throw new Error(body.error);

      const labels = body.hourly.map(h => {
        const d = new Date(h.dt * 1000);
        return d.getHours().toString().padStart(2, '0') + ':00';
      });
      const temps = body.hourly.map(h => h.temp);

      if (hourlyChart) hourlyChart.destroy();

      hourlyChart = new Chart(ctxHourly, {
        type: 'line',
        data: { labels, datasets: [{ label: `Temp (${body.unit})`, data: temps, fill: false, tension: 0.2 }] },
        options: {
          scales: {
            x: { title: { display: true, text: 'Hour' } },
            y: { title: { display: true, text: `Temp (${body.unit})` } }
          },
          plugins: { legend: { display: false } }
        }
      });
      hourlyContainer.style.display = '';
    } catch (err) {
      console.error('❌ Hourly fetch error:', err);
    }
  }

  // 7) Handle form submit: geocode, recenter & fetch
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const city    = cityInput.value.trim();
    const country = countryInput.value.trim();
    console.log('📝 form submit:', { city, country });
    if (!city) {
      console.warn('No city provided; aborting submit.');
      return;
    }

    try {
      const query = encodeURIComponent(city + (country ? ',' + country : ''));
      console.log(`🔍 Geocoding "${query}"…`);
      const r   = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}`);
      const loc = await r.json();
      if (!loc.length) throw new Error('Location not found.');
      const { lat, lon } = loc[0];

      map.setView([+lat, +lon], 8);
      marker.setLatLng([+lat, +lon]);
      await fetchDaily(+lat, +lon);
    } catch (err) {
      console.error('❌ Geocode error:', err);
      alert(err.message);
    }
  });

  // 8) Toggle daily vs hourly
  controlsItems.forEach(item => {
    item.addEventListener('click', e => {
      e.preventDefault();
      const choice = item.dataset.forecast;
      controlsBtn.textContent = `Show: ${item.textContent}`;
      if (choice === 'daily') {
        resultEl.style.display        = '';
        hourlyContainer.style.display = 'none';
      } else {
        resultEl.style.display        = 'none';
        hourlyContainer.style.display = '';
        fetchHourly(lastCoords.lat, lastCoords.lng);
      }
    });
  });

  // 9) Map click & marker drag → reload daily forecast
  map.on('click', e => {
    fetchDaily(e.latlng.lat, e.latlng.lng);
    marker.setLatLng(e.latlng);
  });
  marker.on('dragend', () => {
    const { lat, lng } = marker.getLatLng();
    fetchDaily(lat, lng);
  });

  // 10) Attempt geolocation (user permission)
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      const { latitude, longitude } = pos.coords;
      console.log('🌐 Geolocation success:', { latitude, longitude });
      map.setView([latitude, longitude], 8);
      marker.setLatLng([latitude, longitude]);
      fetchDaily(latitude, longitude);
    }, err => {
      console.warn('🌐 Geolocation failed:', err);
    });
  }

  // 11) Always run default-city search to preload forecast
  function initialSearch() {
    const defaultCity = cityInput.value.trim();
    if (defaultCity) {
      console.log('🏁 initialSearch:', defaultCity);
      form.dispatchEvent(new Event('submit', { bubbles: true }));
    }
  }
  initialSearch();
}

// Self‑initialize on DOMContentLoaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initWeatherMap);
} else {
  initWeatherMap();
}
