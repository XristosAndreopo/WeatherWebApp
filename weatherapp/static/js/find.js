// File: static/js/find.js
// ───────────────────────────────────────────────────────────────────────────────
// Module: Find‑by‑Location (with spinner & debounce)
//
// Responsibilities:
//   1. Toggle daily/hourly forecast views.
//   2. Show spinner while loading hourly data.
//   3. Debounce AJAX fetch to avoid rapid repeat calls.
//   4. Render Chart.js line chart for hourly temps.
// ───────────────────────────────────────────────────────────────────────────────

/**
 * Debounce helper: delay execution until delay ms have passed since last call.
 * @param {Function} fn
 * @param {number} delay
 * @returns {Function}
 */
function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

function initFindDropdown() {
  const container = document.getElementById('findSection');
  if (!container) return;  // Not on Find page

  // DOM refs
  const spinner     = document.getElementById('findSpinner');
  const dropdownBtn = container.querySelector('#forecastDropdown');
  const items       = container.querySelectorAll('.dropdown-item');
  const dailyDiv    = document.getElementById('dailyForecast');
  const hourlyDiv   = document.getElementById('hourlyForecast');
  const canvas      = document.getElementById('findHourlyChart');
  const ctx         = canvas?.getContext('2d');
  let chart         = null;

  // Coordinates injected via data attributes
  const lat = parseFloat(container.dataset.lat);
  const lng = parseFloat(container.dataset.lng);

  function showSpinner() { spinner.style.display = ''; }
  function hideSpinner() { spinner.style.display = 'none'; }

  /**
   * Fetch next‑24h hourly data and render chart.
   */
  async function fetchAndRenderHourly() {
    if (isNaN(lat) || isNaN(lng) || !ctx) return;
    showSpinner();

    try {
      const res  = await fetch(`${window.MAP_HOURLY_URL}?lat=${lat}&lng=${lng}`, {
        credentials: 'same-origin',
        headers: { 'X-CSRFToken': window.CSRF_TOKEN }
      });
      const body = await res.json();
      if (!body.hourly) throw new Error('No hourly data');

      const labels = body.hourly.map(h => {
        const d = new Date(h.dt * 1000);
        return d.getHours().toString().padStart(2, '0') + ':00';
      });
      const temps = body.hourly.map(h => h.temp);

      if (chart) chart.destroy();
      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: `Temp (${body.unit})`,
            data: temps,
            fill: false,
            tension: 0.2
          }]
        },
        options: {
          scales: {
            x: { title: { display:true, text:'Hour' } },
            y: { title: { display:true, text:`Temp (${body.unit})` } }
          },
          plugins: { legend: { display:false } }
        }
      });
    } catch (err) {
      console.error('❌ Find hourly error:', err);
    } finally {
      hideSpinner();
    }
  }

  const debouncedLoad = debounce(fetchAndRenderHourly, 300);

  // Wire up dropdown items
  items.forEach(item => {
    item.addEventListener('click', e => {
      e.preventDefault();
      const choice = item.dataset.forecast;
      dropdownBtn.textContent = `Show: ${item.textContent}`;

      if (choice === 'daily') {
        dailyDiv.style.display  = '';
        hourlyDiv.style.display = 'none';
      } else {
        dailyDiv.style.display  = 'none';
        hourlyDiv.style.display = '';
        debouncedLoad();
      }
    });
  });

  // Initialize on daily view
  dailyDiv.style.display  = '';
  hourlyDiv.style.display = 'none';
}

// Self‑initialize
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initFindDropdown);
} else {
  initFindDropdown();
}
