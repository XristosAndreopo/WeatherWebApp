// File: static/js/map.js
// ───────────────────────────────────────────────────────────────────────────────
// Module: Interactive Weather Map (with debounce & spinner)
//
// Responsibilities:
//   1. Initialize Leaflet map + draggable marker.
//   2. Debounce map interactions to limit API calls.
//   3. Show/hide spinner during daily forecast fetch.
//   4. Render daily cards and hourly chart via AJAX.
//   5. Lazy‑load icons in generated HTML.
// ───────────────────────────────────────────────────────────────────────────────

/**
 * Debounce helper: delay execution until `delay`ms
 * have passed since last invocation.
 */
function debounce(fn, delay = 500) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

async function initWeatherMap() {
  console.log('⚙️ initWeatherMap running…');

  // Preconditions
  if (typeof L === 'undefined' || !document.getElementById('map')) {
    console.warn('Leaflet or #map missing; aborting.');
    return;
  }

  // DOM refs
  const form            = document.getElementById('mapSearchForm');
  const cityInput       = document.getElementById('cityInput');
  const countryInput    = document.getElementById('countryInput');
  const spinner         = document.getElementById('weatherSpinner');
  const resultEl        = document.getElementById('weatherResult');
  const favForm         = document.getElementById('mapAddFavForm');
  const favCityField    = document.getElementById('mapAddFavCity');
  const favCountryField = document.getElementById('mapAddFavCountry');
  const controlsWrapper = document.getElementById('mapForecastControls');
  const controlsBtn     = document.getElementById('mapForecastDropdown');
  const controlsItems   = controlsWrapper.querySelectorAll('.dropdown-item');
  const hourlyContainer = document.getElementById('hourlyMapChartContainer');
  const ctxHourly       = document.getElementById('hourlyMapChart')?.getContext('2d');

  let hourlyChart = null;
  let lastCoords  = { lat: null, lng: null };

  // Initialize map & marker
  const map    = L.map('map').setView([51.505, -0.09], 4);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18 }).addTo(map);
  const marker = L.marker([51.505, -0.09], { draggable: true }).addTo(map);

  // Spinner controls
  function showSpinner() { spinner.style.display = ''; resultEl.style.display = 'none'; }
  function hideSpinner() { spinner.style.display = 'none'; resultEl.style.display = ''; }

  /**
   * Fetch & render the daily forecast.
   * @param {number} lat
   * @param {number} lng
   */
  async function fetchDaily(lat, lng) {
    lastCoords = { lat, lng };
    showSpinner();

    try {
      const res  = await fetch(`${window.MAP_WEATHER_URL}?lat=${lat}&lng=${lng}`, {
        credentials: 'same-origin',
        headers: { 'X-CSRFToken': window.CSRF_TOKEN }
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      // Build HTML
      let html = `<h4>Forecast for ${data.location}</h4><div class="row">`;
      data.forecast.forEach(day => {
        html += `
          <div class="col-md-3 mb-3">
            <div class="card text-center">
              <div class="card-body">
                ${day.error
                  ? `<div class="text-danger">${day.error}</div>`
                  : `
                    <strong>${day.date}</strong><br>
                    <img loading="lazy"
                         src="${window.STATIC_URL}img/weather_icons/${day.icon}"
                         alt="${day.description}" width="48" height="48"><br>
                    ${day.description.charAt(0).toUpperCase()+day.description.slice(1)}<br>
                    Temp: ${day.temp}${data.unit}<br>
                    Humidity: ${day.humidity}%
                  `}
              </div>
            </div>
          </div>`;
      });
      html += `</div>`;
      resultEl.innerHTML = html;

      // Show controls & favorites
      controlsWrapper.style.display = '';
      hourlyContainer.style.display = 'none';
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
    } finally {
      hideSpinner();
    }
  }

  // Debounced wrapper for map events
  const debouncedFetchDaily = debounce(fetchDaily, 500);

  /**
   * Fetch & render the hourly chart.
   * @param {number} lat
   * @param {number} lng
   */
  async function fetchHourly(lat, lng) {
    if (!ctxHourly) return;

    try {
      const res  = await fetch(`${window.MAP_HOURLY_URL}?lat=${lat}&lng=${lng}`, {
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
        data:      { labels, datasets:[{ label:`Temp (${body.unit})`, data:temps, fill:false, tension:0.2 }] },
        options:   {
          scales: {
            x:{ title:{ display:true, text:'Hour' } },
            y:{ title:{ display:true, text:`Temp (${body.unit})` } }
          },
          plugins:{ legend:{ display:false } }
        }
      });
      hourlyContainer.style.display = '';
    } catch (err) {
      console.error('❌ Hourly fetch error:', err);
    }
  }

  // Form submission → geocode → fetchDaily
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const city    = cityInput.value.trim();
    const country = countryInput.value.trim();
    if (!city) return;

    try {
      const query = encodeURIComponent(city + (country ? ',' + country : ''));
      const r     = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}`);
      const loc   = await r.json();
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

  // Daily ↔ Hourly toggle
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

  // Debounced map click & marker drag
  map.on('click', e => debouncedFetchDaily(e.latlng.lat, e.latlng.lng));
  marker.on('dragend', () => {
    const { lat, lng } = marker.getLatLng();
    debouncedFetchDaily(lat, lng);
  });

  // Geolocation on load → otherwise initial default search
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      map.setView([pos.coords.latitude, pos.coords.longitude], 8);
      marker.setLatLng([pos.coords.latitude, pos.coords.longitude]);
      fetchDaily(pos.coords.latitude, pos.coords.longitude);
    }, () => form.dispatchEvent(new Event('submit', { bubbles: true })));
  } else {
    form.dispatchEvent(new Event('submit', { bubbles: true }));
  }
}

// Initialize
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initWeatherMap);
} else {
  initWeatherMap();
}
