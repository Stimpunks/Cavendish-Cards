/* Manual light/dark toggle. Progressive enhancement: the no-flash pre-paint
   inline script in each page already applies a saved choice before first paint;
   this file adds the on-page control so people can flip themes without touching
   OS settings. With no saved choice the site follows the system setting; the
   first flip saves an explicit preference (in localStorage, on this device
   only). See the Privacy & security page. */
(function () {
  var root = document.documentElement;
  var KEY = 'theme';
  var mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function effective() {
    var s = stored();
    if (s === 'dark' || s === 'light') return s;
    return (mq && mq.matches) ? 'dark' : 'light';
  }
  function apply(theme) {
    if (theme === 'dark' || theme === 'light') root.setAttribute('data-theme', theme);
    else root.removeAttribute('data-theme');
  }

  function sync(btn) {
    var isDark = effective() === 'dark';
    btn.setAttribute('aria-pressed', String(isDark));
    btn.querySelector('.theme-toggle-icon').textContent = isDark ? '\u263E' : '\u2600';
    btn.querySelector('.theme-toggle-label').textContent = isDark ? 'Dark' : 'Light';
    btn.setAttribute('aria-label',
      'Appearance: ' + (isDark ? 'dark' : 'light') +
      '. Activate to switch to ' + (isDark ? 'light' : 'dark') + ' mode.');
    btn.setAttribute('title', 'Switch to ' + (isDark ? 'light' : 'dark') + ' mode');
  }

  function build() {
    var nav = document.querySelector('.sitenav');
    if (!nav || document.getElementById('theme-toggle')) return;
    var btn = document.createElement('button');
    btn.id = 'theme-toggle';
    btn.type = 'button';
    btn.className = 'theme-toggle';
    btn.innerHTML = '<span class="theme-toggle-icon" aria-hidden="true"></span>' +
                    '<span class="theme-toggle-label"></span>';
    nav.insertAdjacentElement('afterend', btn);
    sync(btn);
    btn.addEventListener('click', function () {
      var next = effective() === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(KEY, next); } catch (e) {}
      apply(next);
      sync(btn);
    });
    if (mq && mq.addEventListener) {
      mq.addEventListener('change', function () { if (!stored()) sync(btn); });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
