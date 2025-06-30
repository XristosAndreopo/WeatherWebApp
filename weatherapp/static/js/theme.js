<script>
// --- Cookie helpers ---
function getCookie(name) {
    let match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) return match[2];
    return null;
}
function setCookie(name, value, days=365) {
    let expires = "";
    if (days) {
        let d = new Date();
        d.setTime(d.getTime() + (days*24*60*60*1000));
        expires = ";expires=" + d.toUTCString();
    }
    document.cookie = name + "=" + value + expires + ";path=/";
}
// --- Apply theme to page ---
function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
}
// --- On load, sync UI with cookie and apply theme ---
document.addEventListener('DOMContentLoaded', function() {
    let theme = getCookie('theme') || 'light';
    applyTheme(theme);
    document.getElementById('themeSelect').value = theme;

    document.getElementById('applyTheme').onclick = function() {
        let selected = document.getElementById('themeSelect').value;
        setCookie('theme', selected, 365);
        applyTheme(selected);
    }
});
</script>

