(function () {
  'use strict';

  var deckEl, tableEl, emptyEl, clearBtn, doneBtn, filtersEl, blurbEl, momentsRow, liveEl;
  var summaryEl, summaryListEl, summaryCopyBtn, summaryCloseBtn;
  var lightboxEl, lbImg, lbNameEl, lbPromptEl, lbNoteEl, lbNoteTextEl, lbCloseBtn, lbReturn = null;
  var families = [];
  var browseFamilies = [];
  var momentFamilies = [];
  var bySlug = {};
  var active = 'all';
  var laid = [];            // [{slug, up, refIdx}]
  var pendingFocus = null;  // {i, sel} | 'empty' | null

  var ZOOM_SVG =
    '<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" focusable="false">' +
    '<circle cx="8.5" cy="8.5" r="5.5" fill="none" stroke="currentColor" stroke-width="2"></circle>' +
    '<line x1="12.6" y1="12.6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"></line>' +
    '</svg>';

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
  function browseBySlug(slug) {
    for (var i = 0; i < browseFamilies.length; i++) {
      if (browseFamilies[i].slug === slug) return browseFamilies[i];
    }
    return null;
  }

  function reflectionFor(item) {
    var c = bySlug[item.slug];
    if (!c || !c.reflections || !c.reflections.length) return '';
    return c.reflections[(item.refIdx || 0) % c.reflections.length];
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

  function tile(c) {
    var wrap = document.createElement('div');
    wrap.className = 'tile-wrap';

    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'tile';
    b.setAttribute('aria-label', 'Lay ' + c.name + ' on the table');
    b.innerHTML =
      '<span class="tile-art"><img src="' + escAttr(c.face) +
      '" alt="" loading="lazy"></span>' +
      '<span class="tile-name">' + esc(c.name) + '</span>';
    b.addEventListener('click', function () { lay(c.slug); });

    var z = document.createElement('button');
    z.type = 'button';
    z.className = 'zoom';
    z.setAttribute('aria-label', 'Enlarge ' + c.name);
    z.innerHTML = ZOOM_SVG;
    z.addEventListener('click', function () { openLightbox(c, z); });

    wrap.appendChild(b);
    wrap.appendChild(z);
    return wrap;
  }

  function grid(cards) {
    var g = document.createElement('div');
    g.className = 'deck-grid';
    cards.forEach(function (c) { g.appendChild(tile(c)); });
    return g;
  }

  function renderGrouped(fam) {
    fam.groupOrder.forEach(function (label) {
      var inGroup = fam.cards.filter(function (c) { return c.group === label; });
      if (!inGroup.length) return;
      var h = document.createElement('h3');
      h.className = 'deck-group';
      h.textContent = label;
      deckEl.appendChild(h);
      deckEl.appendChild(grid(inGroup));
    });
  }

  function renderDeck() {
    deckEl.innerHTML = '';
    if (active !== 'all') {
      var fam = browseBySlug(active);
      if (fam && fam.groupOrder && fam.groupOrder.length) {
        renderGrouped(fam);
        return;
      }
    }
    var all = [];
    browseFamilies.forEach(function (f) {
      if (active !== 'all' && f.slug !== active) return;
      f.cards.forEach(function (c) { all.push(c); });
    });
    deckEl.appendChild(grid(all));
  }

  function renderMoments() {
    if (!momentsRow) return;
    momentsRow.innerHTML = '';
    momentFamilies.forEach(function (f) {
      f.cards.forEach(function (c) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'moment-chip';
        b.textContent = c.name;
        b.setAttribute('aria-label', 'Lay ' + c.name + ' on the table');
        b.addEventListener('click', function () { lay(c.slug); });
        momentsRow.appendChild(b);
      });
    });
  }

  function lay(slug) {
    laid.push({ slug: slug, up: false, refIdx: 0 });
    pendingFocus = { i: laid.length - 1, sel: '.flip' };
    renderTable();
    announce('Laid ' + bySlug[slug].name + ' on the table, face-down.');
  }

  function updatePlaceBackground() {
    var place = '';
    laid.forEach(function (item) {
      var c = bySlug[item.slug];
      if (item.up && c && c.family === 'places' && item.slug !== 'your-own') place = item.slug;
    });
    if (place) document.body.setAttribute('data-place', place);
    else document.body.removeAttribute('data-place');
  }

  function renderTable() {
    if (summaryEl) summaryEl.hidden = true;
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
        var refl = c.reflections && c.reflections.length ? c.reflections : [];
        var reflHtml = '';
        if (refl.length) {
          reflHtml = '<div class="reflect">' +
            '<p class="reflect-q" aria-live="polite">' + esc(reflectionFor(item)) + '</p>' +
            (refl.length > 1
              ? '<button type="button" class="reflect-more">another question</button>'
              : '') +
            '</div>';
        }
        text = '<div class="laid-text"><span class="laid-name">' +
          esc(c.name) + '</span>' + promptLine + note + reflHtml + '</div>';
      }

      var zoomBtn = item.up
        ? '<button type="button" class="zoom" aria-label="Enlarge ' +
          escAttr(c.name) + '">' + ZOOM_SVG + '</button>'
        : '';

      li.innerHTML =
        '<div class="laid-card"><img class="laid-img" src="' + escAttr(img) +
        '" alt="' + escAttr(alt) + '">' + zoomBtn + '</div>' +
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
      var moreBtn = li.querySelector('.reflect-more');
      if (moreBtn) {
        moreBtn.addEventListener('click', function () {
          laid[i].refIdx = ((laid[i].refIdx || 0) + 1) % c.reflections.length;
          var qEl = li.querySelector('.reflect-q');
          if (qEl) qEl.textContent = reflectionFor(laid[i]);
        });
      }
      var zEl = li.querySelector('.laid-card .zoom');
      if (zEl) zEl.addEventListener('click', function () { openLightbox(c, zEl); });

      tableEl.appendChild(li);
    });

    updatePlaceBackground();
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

  function summaryText() {
    return laid.map(function (item) {
      var c = bySlug[item.slug];
      var line = '- ' + c.name + (c.prompt ? ' — ' + c.prompt : '');
      var q = reflectionFor(item);
      return q ? line + '\n  reflect: ' + q : line;
    }).join('\n');
  }

  function showSummary() {
    if (!summaryEl) return;
    summaryListEl.innerHTML = '';
    laid.forEach(function (item) {
      var c = bySlug[item.slug];
      var name = c.name + (c.prompt ? ' — ' + c.prompt : '');
      var q = reflectionFor(item);
      var li = document.createElement('li');
      li.innerHTML = '<span class="summary-name">' + esc(name) + '</span>' +
        (q ? '<span class="summary-reflect">' + esc(q) + '</span>' : '');
      summaryListEl.appendChild(li);
    });
    summaryEl.hidden = false;
    var h = document.getElementById('summary-h');
    if (h) h.focus();
  }

  function openLightbox(card, trigger) {
    if (!lightboxEl) return;
    lbReturn = trigger || null;
    lbImg.setAttribute('src', card.face);
    lbImg.setAttribute('alt', card.name + (card.prompt ? ': ' + card.prompt : ''));
    lbNameEl.textContent = card.name;
    if (card.prompt) {
      lbPromptEl.textContent = card.prompt; lbPromptEl.hidden = false;
    } else if (card.given_not_read) {
      lbPromptEl.textContent = 'given, not read'; lbPromptEl.hidden = false;
    } else {
      lbPromptEl.textContent = ''; lbPromptEl.hidden = true;
    }
    if (lbNoteEl) {
      if (card.notes) {
        lbNoteTextEl.textContent = card.notes;
        lbNoteEl.open = false;
        lbNoteEl.hidden = false;
      } else {
        lbNoteEl.hidden = true;
      }
    }
    lightboxEl.hidden = false;
    document.body.classList.add('lightbox-open');
    document.addEventListener('keydown', lbKeydown);
    lbCloseBtn.focus();
  }

  function closeLightbox() {
    if (!lightboxEl || lightboxEl.hidden) return;
    lightboxEl.hidden = true;
    document.body.classList.remove('lightbox-open');
    document.removeEventListener('keydown', lbKeydown);
    if (lbReturn && document.body.contains(lbReturn)) lbReturn.focus();
    lbReturn = null;
  }

  function lbKeydown(e) {
    if (e.key === 'Escape') { e.preventDefault(); closeLightbox(); return; }
    if (e.key !== 'Tab') return;
    var found = lightboxEl.querySelectorAll(
      'button, summary, a[href], [tabindex]:not([tabindex="-1"])');
    var els = [];
    for (var i = 0; i < found.length; i++) {
      if (!found[i].disabled && found[i].offsetParent !== null) els.push(found[i]);
    }
    if (!els.length) return;
    var first = els[0], last = els[els.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  function start(data) {
    families = (data && data.families) || [];
    families.forEach(function (f) {
      f.cards.forEach(function (c) {
        c.family = f.slug; c.familyName = f.name; bySlug[c.slug] = c;
      });
    });
    browseFamilies = families.filter(function (f) { return f.mode !== 'moments'; });
    momentFamilies = families.filter(function (f) { return f.mode === 'moments'; });

    filtersEl.appendChild(mkFilter('all', 'All'));
    browseFamilies.forEach(function (f) {
      filtersEl.appendChild(mkFilter(f.slug, f.name));
    });

    clearBtn.addEventListener('click', function () {
      laid = [];
      active = 'all';
      var kids = filtersEl.children;
      for (var i = 0; i < kids.length; i++) {
        kids[i].setAttribute('aria-pressed',
          kids[i].dataset.slug === 'all' ? 'true' : 'false');
      }
      updateBlurb('all');
      pendingFocus = null;
      renderDeck();
      renderTable();
      if (filtersEl.firstChild) filtersEl.firstChild.focus();
      announce('Cleared the table and started over.');
    });

    doneBtn.addEventListener('click', function () {
      if (!laid.length) return;
      laid.forEach(function (x) { x.up = true; });
      pendingFocus = null;
      renderTable();
      showSummary();
      announce('Turned all the cards face-up.');
    });

    if (summaryCopyBtn) {
      summaryCopyBtn.addEventListener('click', function () {
        var text = 'My Cavendish spread\n' + summaryText();
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(
            function () { announce('Copied.'); },
            function () { announce('Could not copy.'); }
          );
        } else {
          announce('Copy is not available in this browser.');
        }
      });
    }
    if (summaryCloseBtn) {
      summaryCloseBtn.addEventListener('click', function () {
        summaryEl.hidden = true;
        doneBtn.focus();
      });
    }

    renderDeck();
    renderMoments();
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
    momentsRow = document.getElementById('moments-row');
    liveEl = document.getElementById('live');
    summaryEl = document.getElementById('summary');
    summaryListEl = document.getElementById('summary-list');
    summaryCopyBtn = document.getElementById('summary-copy');
    summaryCloseBtn = document.getElementById('summary-close');

    lightboxEl = document.getElementById('lightbox');
    lbImg = document.getElementById('lightbox-img');
    lbNameEl = document.getElementById('lightbox-name');
    lbPromptEl = document.getElementById('lightbox-prompt');
    lbCloseBtn = document.getElementById('lightbox-close');
    lbNoteEl = document.getElementById('lightbox-note');
    lbNoteTextEl = document.getElementById('lightbox-note-text');
    if (lightboxEl && lbCloseBtn) {
      lbCloseBtn.addEventListener('click', closeLightbox);
      lightboxEl.addEventListener('click', function (e) {
        if (e.target === lightboxEl ||
            (e.target.hasAttribute && e.target.hasAttribute('data-close'))) {
          closeLightbox();
        }
      });
    }

    var breakToggle = document.getElementById('break-toggle');
    var breakPanel = document.getElementById('break-panel');
    var breakClose = document.getElementById('break-close');
    if (breakToggle && breakPanel) {
      breakToggle.addEventListener('click', function () {
        var opening = breakPanel.hidden;
        breakPanel.hidden = !opening;
        breakToggle.setAttribute('aria-expanded', opening ? 'true' : 'false');
        if (opening && breakClose) breakClose.focus();
      });
      if (breakClose) {
        breakClose.addEventListener('click', function () {
          breakPanel.hidden = true;
          breakToggle.setAttribute('aria-expanded', 'false');
          breakToggle.focus();
        });
      }
    }

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
