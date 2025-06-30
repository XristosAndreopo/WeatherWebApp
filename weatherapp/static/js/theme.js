// weatherapp/static/js/theme.js

// --- Cookie helpers ---
function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

function setCookie(name, value, days = 365) {
  let expires = '';
  if (days) {
    const d = new Date();
    d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
    expires = ';expires=' + d.toUTCString();
  }
  document.cookie = name + '=' + value + expires + ';path=/';
}

// --- Apply theme attribute ---
function applyTheme(theme) {
  document.body.setAttribute('data-theme', theme);
}

// --- On load, sync & wire up ---
document.addEventListener('DOMContentLoaded', function() {
  // 1) Apply from cookie (or default 'light')
  const theme = getCookie('theme') || 'light';
  applyTheme(theme);

  // 2) If on Settings, hook up the <select> + button
  const selectEl = document.getElementById('themeSelect');
  const btn      = document.getElementById('applyTheme');
  if (selectEl && btn) {
    selectEl.value = theme;
    btn.addEventListener('click', function() {
      const newTheme = selectEl.value;
      setCookie('theme', newTheme, 365);
      applyTheme(newTheme);
    });
  }
});
