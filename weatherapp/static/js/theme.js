// File: static/js/theme.js
// ───────────────────────────────────────────────────────────────────────────────
// Module: ThemeManager
//
// Responsibilities:
//   • Read the “theme” cookie (or system preference as fallback) and apply it.
//   • On the settings page, watch for changes to <select id="defaultTheme">.
//   • Persist the user’s choice as a cookie for 365 days.
//   • Applies theme via <html data-theme=""> for consistent theming (avoids FOUC).
// ───────────────────────────────────────────────────────────────────────────────

const ThemeManager = (() => {
  /**
   * Read a named cookie’s value, or null if not found.
   * @param {string} name
   * @returns {string|null}
   */
  function getCookie(name) {
    const match = document.cookie.match(
      new RegExp('(?:^|; )' + name + '=([^;]*)')
    );
    return match ? decodeURIComponent(match[1]) : null;
  }

  /**
   * Write a cookie that lasts `days` (defaults to 365).
   * @param {string} name
   * @param {string} value
   * @param {number} [days=365]
   */
  function setCookie(name, value, days = 365) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires};path=/`;
  }

  /**
   * Determine preferred theme based on cookie or system setting.
   * @returns {string}
   */
  function getPreferredTheme() {
    const saved = getCookie('theme');
    if (saved) return saved;

    // Use browser's preference as fallback
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return systemPrefersDark ? 'dracula' : 'light';
  }

  /**
   * Apply theme to <html data-theme="">
   * @param {string} theme
   */
  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
  }

  /**
   * Initialize theme system once DOM is ready.
   */
  function init() {
    const current = getPreferredTheme();
    apply(current);

    // If on settings page, bind to dropdown
    const sel = document.getElementById('defaultTheme');
    if (sel) {
      sel.value = current;
      sel.addEventListener('change', (e) => {
        const newTheme = e.target.value;
        setCookie('theme', newTheme);
        apply(newTheme);
      });
    }
  }

  // Wait for DOM to be interactive
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Optional: expose API for manual use or debugging
  return { getCookie, setCookie, apply, getPreferredTheme };
})();
