/* KuralBench site: theme, menu, copy buttons, tabs, task filter, sample viewer. No dependencies. */
(function () {
  'use strict';
  var doc = document, root = doc.documentElement;
  var $ = function (s, r) { return (r || doc).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || doc).querySelectorAll(s)); };

  // theme: the inline bootstrap sets data-theme from storage before paint; the button flips it
  var themeBtn = $('[data-theme-toggle]');
  function effective() {
    var t = root.getAttribute('data-theme');
    if (t) return t;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = effective() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('kb-theme', next); } catch (e) { /* storage may be blocked */ }
    });
  }

  // menu
  var menuBtn = $('[data-menu]'), nav = $('#site-nav');
  if (menuBtn && nav) {
    var setMenu = function (open) {
      nav.classList.toggle('open', open);
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    menuBtn.addEventListener('click', function () { setMenu(!nav.classList.contains('open')); });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) { setMenu(false); menuBtn.focus(); }
    });
    $$('a', nav).forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  }

  // copy buttons
  var live = $('#live');
  function announce(msg) {
    if (!live) return;
    live.textContent = '';
    window.setTimeout(function () { live.textContent = msg; }, 30);
  }
  function fallbackCopy(text) {
    var ta = doc.createElement('textarea');
    ta.value = text; ta.setAttribute('readonly', ''); ta.className = 'sr-only';
    doc.body.appendChild(ta); ta.select();
    var ok = false;
    try { ok = doc.execCommand('copy'); } catch (e) { ok = false; }
    doc.body.removeChild(ta);
    return ok;
  }
  $$('[data-copy]').forEach(function (btn) {
    var label = $('span', btn), idle = label.textContent;
    btn.addEventListener('click', function () {
      var src = doc.getElementById(btn.getAttribute('data-copy'));
      if (!src) return;
      var text = src.textContent.replace(/\n$/, '');
      var done = function (ok) {
        label.textContent = ok ? 'Copied' : 'Press Ctrl+C';
        announce(ok ? 'Copied to the clipboard' : 'Copy failed. Select the text and copy it.');
        window.setTimeout(function () { label.textContent = idle; }, 1800);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(fallbackCopy(text)); });
      } else { done(fallbackCopy(text)); }
    });
  });

  // tabs: roving tabindex, arrows, Home, End
  $$('[data-tabs]').forEach(function (box) {
    var tabs = $$('[role="tab"]', box), panels = tabs.map(function (t) { return doc.getElementById(t.getAttribute('aria-controls')); });
    function select(i, focus) {
      tabs.forEach(function (t, j) {
        var on = i === j;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        panels[j].hidden = !on;
      });
      if (focus) tabs[i].focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(i, false); });
      t.addEventListener('keydown', function (e) {
        var n = tabs.length, to = -1;
        if (e.key === 'ArrowRight') to = (i + 1) % n;
        else if (e.key === 'ArrowLeft') to = (i + n - 1) % n;
        else if (e.key === 'Home') to = 0;
        else if (e.key === 'End') to = n - 1;
        if (to >= 0) { e.preventDefault(); select(to, true); }
      });
    });
  });

  // task filter
  var filters = $$('[data-filter]');
  if (filters.length) {
    var groups = $$('.tgroup[data-track]');
    var apply = function (k) {
      filters.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-filter') === k ? 'true' : 'false'); });
      groups.forEach(function (g) { g.hidden = !(k === 'all' || g.getAttribute('data-track') === k); });
      announce(k === 'all' ? 'Showing all tracks' : 'Showing the ' + k + ' track');
    };
    filters.forEach(function (b) { b.addEventListener('click', function () { apply(b.getAttribute('data-filter')); }); });
    var h = (location.hash || '').replace('#g-', '');
    if (h && filters.some(function (b) { return b.getAttribute('data-filter') === h; })) apply(h);
  }

  // sample viewer
  var viewer = $('[data-viewer]'), dataEl = $('#samples-data');
  if (viewer && dataEl) {
    var data;
    try { data = JSON.parse(dataEl.textContent); } catch (e) { return; }
    var items = data.items, i = 0, shown = false;
    var TA = /[஀-௿](?:[஀-௿‌‍ ]*[஀-௿‌‍])?/g, TA1 = /[஀-௿]/, LATIN = /[A-Za-z]/, ROW = /^(\d+)\. (\S.*)$/;
    var SVG = 'http://www.w3.org/2000/svg';
    var el = function (tag, cls, text) {
      var n = doc.createElement(tag);
      if (cls) n.className = cls;
      if (text != null) n.textContent = text;
      return n;
    };
    var tamil = function (node, s) {
      var pos = 0, m;
      TA.lastIndex = 0;
      while ((m = TA.exec(s))) {
        if (m.index > pos) node.appendChild(doc.createTextNode(s.slice(pos, m.index)));
        var sp = el('span', null, m[0]); sp.setAttribute('lang', 'ta'); node.appendChild(sp);
        pos = m.index + m[0].length;
      }
      if (pos < s.length) node.appendChild(doc.createTextNode(s.slice(pos)));
      return node;
    };
    // same structure as rich() in tools/site/build.py: verse, seer list or paragraph per blank-line block
    var rich = function (node, s) {
      String(s).split('\n\n').forEach(function (para) {
        var lines = para.split('\n'), rows = lines.map(function (l) { return ROW.exec(l); });
        if (lines.length > 1 && rows.every(Boolean)) {
          var ol = el('ol', 'seer-list');
          rows.forEach(function (m) {
            var li = el('li'); li.appendChild(el('span', 'sl-n', m[1])); li.appendChild(tamil(el('span', 'sl-w'), m[2]));
            ol.appendChild(li);
          });
          node.appendChild(ol);
        } else if (TA1.test(para) && !LATIN.test(para)) {
          var v = el('div', 'verse'); v.setAttribute('lang', 'ta');
          lines.forEach(function (l) { v.appendChild(el('span', 'verse-l', l)); });
          node.appendChild(v);
        } else {
          var p = el('p');
          lines.forEach(function (l, j) { if (j) p.appendChild(el('br')); tamil(p, l); });
          node.appendChild(p);
        }
      });
      return node;
    };
    var arrow = function (d) {
      var s = doc.createElementNS(SVG, 'svg'); s.setAttribute('viewBox', '0 0 16 16'); s.setAttribute('aria-hidden', 'true');
      var path = doc.createElementNS(SVG, 'path');
      path.setAttribute('d', d); path.setAttribute('fill', 'none'); path.setAttribute('stroke', 'currentColor');
      path.setAttribute('stroke-width', '1.5'); path.setAttribute('stroke-linecap', 'round'); path.setAttribute('stroke-linejoin', 'round');
      s.appendChild(path); return s;
    };
    var navBtn = function (label, d) {
      var b = el('button', 'btn btn-quiet btn-sm btn-icon'); b.type = 'button'; b.setAttribute('aria-label', label);
      b.appendChild(arrow(d)); return b;
    };
    var block = function (title, cls) {
      var b = el('div', 's-block' + (cls ? ' ' + cls : '')); b.appendChild(el('h4', null, title)); return b;
    };
    var prev = navBtn('Previous item', 'M10 4 6 8l4 4'), next = navBtn('Next item', 'm6 4 4 4-4 4');
    var count = el('span', 'v-count'); count.setAttribute('aria-live', 'polite');
    var body = el('div');
    viewer.textContent = '';
    viewer.appendChild(body);

    var render = function () {
      var it = items[i];
      count.textContent = 'Item ' + (i + 1) + ' of ' + items.length;
      body.textContent = '';
      var card = el('article', 'sample'); card.setAttribute('aria-label', 'Sample item ' + (i + 1) + ' of ' + items.length);
      var head = el('div', 's-head'), idp = el('p', 's-id');
      idp.appendChild(el('code', null, it.id)); idp.appendChild(count);
      var navg = el('div', 'v-nav'); navg.appendChild(prev); navg.appendChild(next);
      head.appendChild(idp); head.appendChild(navg); card.appendChild(head);
      var inner = el('div', 's-body');
      var sys = block('System', 's-sys'); sys.appendChild(tamil(el('p'), it.system)); inner.appendChild(sys);
      var pr = block('Prompt'); pr.appendChild(rich(el('div', 's-text s-prompt'), it.prompt)); inner.appendChild(pr);
      var keyLi = null;
      if (it.choices) {
        var ch = block('Choices'), ol = el('ol', 'choices');
        it.choices.forEach(function (c, j) {
          var li = el('li');
          li.appendChild(el('span', 'ch-l', 'ABCD'.charAt(j)));
          li.appendChild(rich(el('div', 'ch-t'), c));
          if (j === it.key) keyLi = li;
          ol.appendChild(li);
        });
        ch.appendChild(ol); inner.appendChild(ch);
      } else {
        var ex = block('Expected format');
        ex.appendChild(el('p', null, viewer.getAttribute('data-format') || ''));
        inner.appendChild(ex);
      }
      var btn = el('button', 'btn btn-quiet btn-sm', shown ? 'Hide answer' : 'Show answer');
      btn.type = 'button'; btn.setAttribute('aria-expanded', shown ? 'true' : 'false');
      var ansBox = el('div', 's-ans-box'); ansBox.hidden = !shown;
      if (it.choices) {
        ansBox.appendChild(el('p', 's-label', 'Answer ' + it.answer + ', marked above'));
      } else if (it.answer) {
        ansBox.appendChild(el('p', 's-label', 'Gold answer'));
        ansBox.appendChild(rich(el('div', 's-text'), it.answer));
      } else {
        ansBox.appendChild(el('p', 's-ans', data.open_note || 'Open task: no gold answer.'));
      }
      var mark = function () { if (keyLi) keyLi.classList.toggle('is-key', shown); };
      btn.addEventListener('click', function () {
        shown = !shown; ansBox.hidden = !shown; btn.textContent = shown ? 'Hide answer' : 'Show answer';
        btn.setAttribute('aria-expanded', shown ? 'true' : 'false'); mark();
      });
      var wrap = el('div', 's-det'); wrap.appendChild(btn); wrap.appendChild(ansBox);
      inner.appendChild(wrap); card.appendChild(inner); body.appendChild(card); mark();
    };
    var go = function (d) { i = (i + d + items.length) % items.length; shown = false; render(); };
    prev.addEventListener('click', function () { go(-1); });
    next.addEventListener('click', function () { go(1); });
    render();
  }
})();
