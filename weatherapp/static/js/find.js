// File: static/js/find.js
// ───────────────────────────────────────────────────────────────────────────────
// Module: Find‑by‑Location toggle (self‑initializing)
// Responsibilities:
//   - Switch between daily and hourly forecasts on the “Find by Location” page.
//   - Fetch & render hourly data via AJAX when “Next 24 Hrs” is selected.
// Self‑init logic at the bottom ensures it runs without any extra bootstrapping.
// ───────────────────────────────────────────────────────────────────────────────

/**
 * Read city/coords from #findSection, wire up dropdown & fetch chart.
 */
function initFindDropdown() {
  const container   = document.getElementById('findSection');
  if (!container) return;  // Bail if we're not on the Find page

  const dropdownBtn = container.querySelector('#forecastDropdown');
  const items       = container.querySelectorAll('.dropdown-item');
  const dailyDiv    = document.getElementById('dailyForecast');
  const hourlyDiv   = document.getElementById('hourlyForecast');
  const canvas      = document.getElementById('findHourlyChart');
  const ctx         = canvas?.getContext('2d');
  let chart         = null;

  // Read the server‑injected latitude/longitude
  const lat = parseFloat(container.dataset.lat);
  const lng = parseFloat(container.dataset.lng);

  /**
   * Fetch next 24h hourly data and render a Chart.js line chart.
   */
  async function fetchAndRenderHourly() {
    if (isNaN(lat) || isNaN(lng) || !ctx) return;

    try {
      const res  = await fetch(
        `${window.MAP_HOURLY_URL}?lat=${lat}&lng=${lng}`, {
          credentials: 'same-origin',
          headers: { 'X-CSRFToken': window.CSRF_TOKEN }
        }
      );
      const body = await res.json();
      if (!body.hourly) return;

      // Prepare data arrays
      const labels = body.hourly.map(h => {
        const d = new Date(h.dt * 1000);
        return d.getHours().toString().padStart(2, '0') + ':00';
      });
      const temps = body.hourly.map(h => h.temp);

      // Destroy any existing chart to avoid memory leaks
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
            x: { title: { display: true, text: 'Hour' } },
            y: { title: { display: true, text: `Temp (${body.unit})` } }
          },
          plugins: { legend: { display: false } }
        }
      });
    } catch (err) {
      console.error('Error fetching hourly forecast:', err);
    }
  }

  // Wire up click on each dropdown item
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
        fetchAndRenderHourly();
      }
    });
  });

  // Initialise: show daily, hide hourly
  dailyDiv.style.display  = '';
  hourlyDiv.style.display = 'none';
}

// ─── Self‑initialize ──────────────────────────────────────────────────────────
// If the DOM is still loading, wait for it; otherwise run immediately.
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initFindDropdown);
} else {
  initFindDropdown();
}
