// colomr-v1 — JS principal

// --- Hamburger / Drawer ---
document.addEventListener('DOMContentLoaded', function () {
  const hamburger = document.getElementById('nav-hamburger');
  const drawer    = document.getElementById('nav-drawer');
  const overlay   = document.getElementById('nav-overlay');

  if (!hamburger) return;

  function openDrawer() {
    drawer.classList.add('is-open');
    overlay.classList.add('is-open');
    hamburger.setAttribute('aria-expanded', 'true');
    drawer.setAttribute('aria-hidden', 'false');
  }

  function closeDrawer() {
    drawer.classList.remove('is-open');
    overlay.classList.remove('is-open');
    hamburger.setAttribute('aria-expanded', 'false');
    drawer.setAttribute('aria-hidden', 'true');
  }

  hamburger.addEventListener('click', function () {
    drawer.classList.contains('is-open') ? closeDrawer() : openDrawer();
  });

  overlay.addEventListener('click', closeDrawer);

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeDrawer();
  });
});

// --- Tabs (formación) ---
document.addEventListener('DOMContentLoaded', function () {
  const tabs = document.querySelectorAll('.ftabs__tab');
  if (!tabs.length) return;

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      const id = tab.dataset.tab;

      tabs.forEach(function (t) {
        t.classList.remove('ftabs__tab--active');
        t.setAttribute('aria-selected', 'false');
      });
      document.querySelectorAll('.ftabs__panel').forEach(function (p) {
        p.classList.remove('ftabs__panel--active');
      });

      tab.classList.add('ftabs__tab--active');
      tab.setAttribute('aria-selected', 'true');
      document.getElementById('tab-' + id).classList.add('ftabs__panel--active');
    });
  });
});

// --- Dark / Light mode toggle ---
(function () {
  const STORAGE_KEY = 'colomr-theme';
  const root = document.documentElement;

  function getPreferred() {
    return localStorage.getItem(STORAGE_KEY) || 'dark';
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }

  applyTheme(getPreferred());

  window.__toggleTheme = function () {
    applyTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
  };
})();
