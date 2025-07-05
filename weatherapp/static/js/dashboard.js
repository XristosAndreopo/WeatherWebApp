// File: static/js/dashboard.js
// ───────────────────────────────────────────────────────────────────────────────
// Module: Dashboard utilities
// Responsibilities:
//   1. Show a random weather-inspired quote on the home/dashboard page.
//   2. Wire up the “days to show” slider on the daily forecast cards.
// Usage:
//   - Imported as a module in base.html and initialized on DOMContentLoaded.
//   - No global state; pure functions and event handlers.
// ───────────────────────────────────────────────────────────────────────────────

// --- Quote rotation ------------------------------------------------------------

/**
 * A small library of uplifting weather quotes.
 * Feel free to add, remove, or tweak these to change the “personality” of your app.
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
 * Pick one quote at random and inject it into the element with ID "weatherQuote".
 * @returns {void}
 */
export function initDashboardQuotes() {
  const el = document.getElementById('weatherQuote');
  if (!el) {
    // No dashboard quote container found; nothing to do.
    return;
  }
  // Random index in [0, QUOTES.length)
  const idx = Math.floor(Math.random() * QUOTES.length);
  el.textContent = QUOTES[idx];
}

// --- Forecast slider -----------------------------------------------------------

/**
 * Slider control to limit number of forecast cards shown.
 * - Expects:
 *     <input type="range" id="daySlider" min="1" max="{totalDays}">
 *     <span id="sliderValue"></span>
 *     Cards with class "forecast-day" in order.
 * @returns {void}
 */
export function initForecastSlider() {
  const slider = document.getElementById('daySlider');
  const label  = document.getElementById('sliderValue');
  const cards  = Array.from(document.querySelectorAll('.forecast-day'));

  if (!slider || !label || cards.length === 0) {
    // Required DOM not present (e.g. on non-dashboard pages)
    return;
  }

  /**
   * Read the slider’s numeric value and show only that many forecast cards.
   */
  function update() {
    const n = parseInt(slider.value, 10);
    label.textContent = n;  // live-update the label next to the slider
    // Show first n cards, hide the rest
    cards.forEach((card, i) => {
      card.style.display = (i < n) ? '' : 'none';
    });
  }

  // Recompute on every input event (slider drag or click)
  slider.addEventListener('input', update);
  // Initialize to the correct state on load
  update();
}

// --- Module entrypoint ---------------------------------------------------------

/**
 * Automatically invoked on page load. Ties together dashboard features.
 */
export function initDashboard() {
  initDashboardQuotes();
  initForecastSlider();
}
