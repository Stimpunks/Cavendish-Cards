(function () {
  'use strict';

  var deckEl, tableEl, emptyEl, clearBtn, doneBtn, filtersEl, blurbEl, liveEl, toTableBtn;
  var summaryEl, summaryListEl, summaryCopyBtn, summaryCloseBtn;
  var lightboxEl, lbImg, lbNameEl, lbPromptEl, lbNoteEl, lbNoteTextEl, lbBuildEl, lbBuildLinkEl, lbCloseBtn, lbReturn = null;
  var families = [];
  var browseFamilies = [];
  var byUid = {};
  var active = 'all';
  var laid = [];            // [{uid, up, refIdx}]
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
    var c = byUid[item.uid];
    if (!c || !c.reflections || !c.reflections.length) return '';
    return c.reflections[(item.refIdx || 0) % c.reflections.length];
  }

  function isLaid(uid) {
    for (var i = 0; i < laid.length; i++) {
      if (laid[i].uid === uid) return true;
    }
    return false;
  }

  function markAdded() {
    var tiles = document.querySelectorAll('.tile');
    for (var i = 0; i < tiles.length; i++) {
      var t = tiles[i];
      var uid = t.dataset.uid;
      if (!uid) continue;
      var on = isLaid(uid);
      var nm = byUid[uid] ? byUid[uid].name : uid;
      t.classList.toggle('tile-added', on);
      t.setAttribute('aria-label',
        on ? ('Take ' + nm + ' back off the table') : ('Lay ' + nm + ' on the table'));
    }
  }

  function updateBlurb(slug) {
    if (slug === 'all') { blurbEl.hidden = true; blurbEl.innerHTML = ''; return; }
    var fam = familyBySlug(slug);
    if (fam && (fam.intro || fam.subtitle)) {
      var html = fam.intro ? esc(fam.intro) : '';
      if (fam.subtitle) {
        html += '<span class="family-subtitle">' + esc(fam.subtitle) + '</span>';
      }
      blurbEl.innerHTML = html;
      blurbEl.hidden = false;
    } else {
      blurbEl.hidden = true; blurbEl.innerHTML = '';
    }
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
    b.dataset.uid = c.uid;
    b.setAttribute('aria-label', 'Lay ' + c.name + ' on the table');
    b.innerHTML =
      '<span class="tile-art"><img src="' + escAttr(c.face) +
      '" alt="" loading="lazy"></span>' +
      '<span class="tile-name">' + esc(c.name) + '</span>';
    b.addEventListener('click', function () { lay(c.uid); });

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
      } else if (fam) {
        deckEl.appendChild(grid(fam.cards));
      }
      markAdded();
      return;
    }
    // "All": one section per realm (heading + flat grid, no sense signposts).
    browseFamilies.forEach(function (f) {
      if (!f.cards.length) return;
      var hasDesc = !!(f.intro || f.subtitle);
      var descId = 'realm-desc-' + f.slug;

      var head = document.createElement('div');
      head.className = 'deck-realm-head';
      var h = document.createElement('h3');
      h.className = 'deck-realm';
      h.textContent = f.name;
      head.appendChild(h);

      var info = null;
      if (hasDesc) {
        info = document.createElement('button');
        info.type = 'button';
        info.className = 'realm-info';
        info.textContent = 'i';
        info.setAttribute('aria-label', 'What is ' + f.name + '?');
        info.setAttribute('aria-expanded', 'false');
        info.setAttribute('aria-controls', descId);
        head.appendChild(info);
      }
      deckEl.appendChild(head);

      if (hasDesc) {
        var desc = document.createElement('div');
        desc.id = descId;
        desc.className = 'realm-desc';
        desc.hidden = true;
        var dhtml = f.intro ? '<p>' + esc(f.intro) + '</p>' : '';
        if (f.subtitle) dhtml += '<p class="family-subtitle">' + esc(f.subtitle) + '</p>';
        desc.innerHTML = dhtml;
        deckEl.appendChild(desc);
        info.addEventListener('click', function () {
          var open = desc.hidden;
          desc.hidden = !open;
          info.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
      }

      deckEl.appendChild(grid(f.cards));
    });
    markAdded();
  }

  function unlay(uid) {
    for (var i = 0; i < laid.length; i++) {
      if (laid[i].uid === uid) { laid.splice(i, 1); break; }
    }
    pendingFocus = null;               // stay in the deck; focus stays on the tile
    renderTable();
    announce('Removed ' + byUid[uid].name + ' from the table.');
  }

  function lay(uid) {
    if (isLaid(uid)) { unlay(uid); return; }
    var c = byUid[uid];
    var start = 0;                      // vary the question so a spread doesn't repeat
    if (c && c.reflections && c.reflections.length > 1) {
      var same = 0;
      for (var i = 0; i < laid.length; i++) {
        var lc = byUid[laid[i].uid];
        if (lc && lc.reflections && lc.reflections.length &&
            lc.reflections[0] === c.reflections[0]) same++;
      }
      start = same % c.reflections.length;
    }
    laid.push({ uid: uid, up: false, refIdx: start });
    pendingFocus = null;               // stay in the deck; don't scroll to the table
    renderTable();
    announce('Laid ' + byUid[uid].name + ' on the table, face-down.');
  }

  function updatePlaceBackground() {
    var place = '';
    laid.forEach(function (item) {
      var c = byUid[item.uid];
      if (item.up && c && c.family === 'places' && c.slug !== 'your-own') place = c.slug;
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
      var c = byUid[item.uid];
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
          : '';
        var buildLink = c.buildLink
          ? '<p class="laid-build"><a href="' + esc(c.buildLink.href) + '">' +
            esc(c.buildLink.label) + ' \u2192</a></p>'
          : '';
        var note = c.notes
          ? '<details class="laid-note"><summary>What this card means</summary><p>' +
            esc(c.notes) + '</p>' + buildLink + '</details>'
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
    if (toTableBtn) {
      toTableBtn.hidden = laid.length === 0;
      toTableBtn.textContent = '↓ Table (' + laid.length + ')';
      toTableBtn.setAttribute('aria-label',
        'Go to the table (' + laid.length + (laid.length === 1 ? ' card' : ' cards') + ')');
    }
    markAdded();
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
      var c = byUid[item.uid];
      var line = '- ' + c.name + (c.prompt ? ' — ' + c.prompt : '');
      var q = reflectionFor(item);
      return q ? line + '\n  reflect: ' + q : line;
    }).join('\n');
  }

  function showSummary() {
    if (!summaryEl) return;
    summaryListEl.innerHTML = '';
    laid.forEach(function (item) {
      var c = byUid[item.uid];
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
    } else {
      lbPromptEl.textContent = ''; lbPromptEl.hidden = true;
    }
    if (lbNoteEl) {
      if (card.notes) {
        lbNoteTextEl.textContent = card.notes;
        if (lbBuildEl) {
          if (card.buildLink) {
            lbBuildLinkEl.href = card.buildLink.href;
            lbBuildLinkEl.textContent = card.buildLink.label + ' \u2192';
            lbBuildEl.hidden = false;
          } else {
            lbBuildEl.hidden = true;
          }
        }
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
        c.family = f.slug; c.familyName = f.name;
        c.uid = f.slug + '/' + c.slug;
        byUid[c.uid] = c;
      });
    });
    browseFamilies = families;

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
    toTableBtn = document.getElementById('to-table');
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
    lbBuildEl = document.getElementById('lightbox-build');
    lbBuildLinkEl = document.getElementById('lightbox-build-link');
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

    if (toTableBtn) {
      toTableBtn.addEventListener('click', function () {
        var h = document.getElementById('table-h');
        if (!h) return;
        h.setAttribute('tabindex', '-1');
        var reduce = window.matchMedia &&
          window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        h.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
        h.focus({ preventScroll: true });
      });
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
