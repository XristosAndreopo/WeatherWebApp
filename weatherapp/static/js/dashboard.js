// File: static/js/dashboard.js
// ───────────────────────────────────────────────────────────────────────────────
// Module: Dashboard utilities (self‑initializing)
//
// Responsibilities:
//   • Display a random weather‑inspired quote in the element with ID "weatherQuote".
//   • Wire up a slider control (#daySlider) to limit visible daily‑forecast cards.
//   • Automatically initialize both features on DOMContentLoaded.
//
// Usage:
//   • Include this as an ES module in base.html after the DOM node with id="weatherQuote":
//       <script type="module" src="{% static 'js/dashboard.js' %}"></script>
//   • No additional inline scripts required.
// ───────────────────────────────────────────────────────────────────────────────

/**
 * A collection of uplifting weather‑themed quotes.
 * Feel free to add, remove, or modify entries for your app’s tone.
 */
const QUOTES = [
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

/**
 * initDashboardQuotes
 * -------------------
 * Selects a random quote from QUOTES and injects it into
 * the DOM element with id="weatherQuote", if present.
 */
export function initDashboardQuotes() {
  const el = document.getElementById('weatherQuote');
  if (!el) {
    // No quote container on this page; nothing to do.
    return;
  }
  const index = Math.floor(Math.random() * QUOTES.length);
  el.textContent = QUOTES[index];
}

/**
 * initForecastSlider
 * ------------------
 * Sets up a <input type="range" id="daySlider"> slider to control
 * how many elements with class "forecast-day" are visible.
 *
 * Expected markup:
 *   <input id="daySlider" type="range" min="1" max="{totalDays}" value="{totalDays}">
 *   <span id="sliderValue">{totalDays}</span>
 *   <div class="forecast-day">…</div>  (one per day)
 */
export function initForecastSlider() {
  const slider = document.getElementById('daySlider');
  const label  = document.getElementById('sliderValue');
  const cards  = Array.from(document.querySelectorAll('.forecast-day'));

  if (!slider || !label || cards.length === 0) {
    // Required elements not present; skip slider setup.
    return;
  }

  // Update function: show the first N cards, hide the rest.
  function update() {
    const n = parseInt(slider.value, 10);
    label.textContent = n;
    cards.forEach((card, i) => {
      card.style.display = i < n ? '' : 'none';
    });
  }

  slider.addEventListener('input', update);
  update();  // Initialize on load
}

/**
 * initDashboard
 * -------------
 * Entry point to initialize dashboard features:
 *   • initDashboardQuotes
 *   • initForecastSlider
 */
export function initDashboard() {
  initDashboardQuotes();
  initForecastSlider();
}

// Auto‑initialize when the DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDashboard);
} else {
  initDashboard();
}
