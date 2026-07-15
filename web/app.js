(function () {
  'use strict';

  var deckEl, tableEl, emptyEl, clearBtn, doneBtn, filtersEl, blurbEl, liveEl;
  var families = [];
  var bySlug = {};
  var active = 'all';
  var laid = [];            // [{slug, up}]
  var pendingFocus = null;  // {i, sel} | 'empty' | null

  function esc(s) {
    return String(s).replace(/[&<>]/g, function (m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[m];
    });
  }
  function escAttr(s) { return esc(s).replace(/"/g, '&quot;'); }

  function announce(msg) {
    liveEl.textContent = '';
    window.setTimeout(function () { liveEl.textContent = msg; }, 30);
  }

  function familyBySlug(slug) {
    for (var i = 0; i < families.length; i++) {
      if (families[i].slug === slug) return families[i];
    }
    return null;
  }

  function updateBlurb(slug) {
    if (slug === 'all') { blurbEl.hidden = true; blurbEl.textContent = ''; return; }
    var fam = familyBySlug(slug);
    if (fam && fam.intro) { blurbEl.textContent = fam.intro; blurbEl.hidden = false; }
    else { blurbEl.hidden = true; blurbEl.textContent = ''; }
  }

  function mkFilter(slug, label) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'filter';
    b.textContent = label;
    b.dataset.slug = slug;
    b.setAttribute('aria-pressed', slug === active ? 'true' : 'false');
    b.addEventListener('click', function () {
      active = slug;
      var kids = filtersEl.children;
      for (var i = 0; i < kids.length; i++) {
        kids[i].setAttribute('aria-pressed',
          kids[i].dataset.slug === slug ? 'true' : 'false');
      }
      updateBlurb(slug);
      renderDeck();
    });
    return b;
  }

  function renderDeck() {
    deckEl.innerHTML = '';
    families.forEach(function (f) {
      if (active !== 'all' && f.slug !== active) return;
      f.cards.forEach(function (c) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'tile';
        b.setAttribute('aria-label', 'Lay ' + c.name + ' on the table');
        b.innerHTML =
          '<span class="tile-art"><img src="' + escAttr(c.face) +
          '" alt="" loading="lazy"></span>' +
          '<span class="tile-name">' + esc(c.name) + '</span>';
        b.addEventListener('click', function () { lay(c.slug); });
        deckEl.appendChild(b);
      });
    });
  }

  function lay(slug) {
    laid.push({ slug: slug, up: false });
    pendingFocus = { i: laid.length - 1, sel: '.flip' };
    renderTable();
    announce('Laid ' + bySlug[slug].name + ' on the table, face-down.');
  }

  function renderTable() {
    tableEl.innerHTML = '';
    emptyEl.hidden = laid.length > 0;
    clearBtn.hidden = laid.length === 0;
    doneBtn.hidden = laid.length === 0;

    laid.forEach(function (item, i) {
      var c = bySlug[item.slug];
      var li = document.createElement('li');
      li.className = 'laid' + (item.up ? ' is-up' : '');

      var img = item.up ? c.face : c.back;
      var alt = item.up
        ? (c.name + (c.prompt ? ': ' + c.prompt : ''))
        : 'Face-down card';

      var text = '';
      if (item.up) {
        var promptLine = c.prompt
          ? '<span class="laid-prompt">' + esc(c.prompt) + '</span>'
          : (c.given_not_read
              ? '<span class="laid-prompt muted">given, not read</span>' : '');
        var note = c.notes
          ? '<details class="laid-note"><summary>What this card means</summary><p>' +
            esc(c.notes) + '</p></details>'
          : '';
        text = '<div class="laid-text"><span class="laid-name">' +
          esc(c.name) + '</span>' + promptLine + note + '</div>';
      }

      li.innerHTML =
        '<div class="laid-card"><img class="laid-img" src="' + escAttr(img) +
        '" alt="' + escAttr(alt) + '"></div>' +
        '<div class="laid-controls">' +
          '<button type="button" class="btn flip">' +
          (item.up ? 'Turn face-down' : 'Turn it up') + '</button>' +
          text +
          '<button type="button" class="btn ghost remove">Remove</button>' +
        '</div>';

      li.querySelector('.flip').addEventListener('click', function () {
        laid[i].up = !laid[i].up;
        pendingFocus = { i: i, sel: '.flip' };
        renderTable();
        announce(laid[i].up
          ? 'Turned up ' + c.name + '.'
          : 'Turned ' + c.name + ' face-down.');
      });
      li.querySelector('.remove').addEventListener('click', function () {
        var nm = c.name;
        laid.splice(i, 1);
        pendingFocus = laid.length
          ? { i: Math.min(i, laid.length - 1), sel: '.flip' }
          : 'empty';
        renderTable();
        announce('Removed ' + nm + ' from the table.');
      });

      tableEl.appendChild(li);
    });

    applyFocus();
  }

  function applyFocus() {
    if (!pendingFocus) return;
    if (pendingFocus === 'empty') {
      var h = document.getElementById('table-h');
      if (h) { h.setAttribute('tabindex', '-1'); h.focus(); }
    } else {
      var li = tableEl.children[pendingFocus.i];
      var el = li && li.querySelector(pendingFocus.sel);
      if (el) el.focus();
    }
    pendingFocus = null;
  }

  function start(data) {
    families = (data && data.families) || [];
    families.forEach(function (f) {
      f.cards.forEach(function (c) {
        c.family = f.slug; c.familyName = f.name; bySlug[c.slug] = c;
      });
    });

    filtersEl.appendChild(mkFilter('all', 'All'));
    families.forEach(function (f) {
      filtersEl.appendChild(mkFilter(f.slug, f.name));
    });

    clearBtn.addEventListener('click', function () {
      laid = [];
      pendingFocus = 'empty';
      renderTable();
      announce('Cleared the table.');
    });

    doneBtn.addEventListener('click', function () {
      if (!laid.length) return;
      laid.forEach(function (x) { x.up = true; });
      pendingFocus = null;
      renderTable();
      announce('Turned all the cards face-up.');
    });

    renderDeck();
    renderTable();
  }

  document.addEventListener('DOMContentLoaded', function () {
    deckEl = document.getElementById('deck');
    tableEl = document.getElementById('table');
    emptyEl = document.getElementById('table-empty');
    clearBtn = document.getElementById('clear');
    doneBtn = document.getElementById('done');
    filtersEl = document.getElementById('filters');
    blurbEl = document.getElementById('family-blurb');
    liveEl = document.getElementById('live');

    fetch('cards.json')
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(start)
      .catch(function () {
        deckEl.innerHTML =
          '<p class="error">Could not load the deck. If you are opening this ' +
          'file directly, serve the <code>web/</code> folder over http instead ' +
          '(see <code>web/README.md</code>).</p>';
      });
  });
})();
