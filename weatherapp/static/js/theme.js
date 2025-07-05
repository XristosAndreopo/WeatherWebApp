// File: static/js/theme.js
// ───────────────────────────────────────────────────────────────────────────────
// Module: ThemeManager
//
// Responsibilities:
//   • Read the “theme” cookie (or default to “light”) and apply it to <body>.
//   • On the settings page, watch for changes to the <select id="defaultTheme">,
//     set the cookie, and apply the new theme live.
//   • Ensures the user’s choice is persisted (365-day cookie).
// ───────────────────────────────────────────────────────────────────────────────

const ThemeManager = (() => {
  /**
   * Read a named cookie’s value, or null if missing.
   * @param {string} name
   * @returns {string|null}
   */
  function getCookie(name) {
    const match = document.cookie.match(
      new RegExp('(^| )' + name + '=([^;]+)')
    );
    return match ? match[2] : null;
  }

  /**
   * Write a cookie that lives `days` days (defaults to 365).
   * @param {string} name
   * @param {string} value
   * @param {number} days
   */
  function setCookie(name, value, days = 365) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${value};expires=${expires};path=/`;
  }

  /**
   * Apply a theme by setting data-theme on <body>.
   * @param {string} theme
   */
  function apply(theme) {
    document.body.setAttribute('data-theme', theme);
  }

  // When the DOM is ready, apply the saved theme and wire up the selector
  document.addEventListener('DOMContentLoaded', () => {
    // 1) Read saved cookie or default to 'light'
    const current = getCookie('theme') || 'light';
    apply(current);

    // 2) Look for your settings dropdown by its ID
    const sel = document.getElementById('defaultTheme');
    if (sel) {
      // Initialize the select to the current theme
      sel.value = current;

      // On change, persist the new theme and apply it immediately
      sel.addEventListener('change', (e) => {
        const newTheme = e.target.value;
        setCookie('theme', newTheme);
        apply(newTheme);
      });
    }
  });

  // Expose for debugging or manual calls if needed
  return { getCookie, setCookie, apply };
})();
