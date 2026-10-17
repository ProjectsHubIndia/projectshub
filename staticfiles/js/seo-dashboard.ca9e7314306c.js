/* ProjectsHub — admin SEO dashboard interactions (filtering, row details) */
(function () {
  'use strict';
  var root = document.getElementById('seoDash');
  if (!root) return;
  var rows = Array.prototype.slice.call(root.querySelectorAll('.sd-row'));
  var chips = root.querySelectorAll('.sd-chip');
  var search = document.getElementById('sdSearch');
  var shown = document.getElementById('sdShown');
  var state = { filter: 'all', q: '', check: '' };

  function apply() {
    var n = 0;
    rows.forEach(function (row) {
      var crit = +row.dataset.crit, warn = +row.dataset.warn;
      var ok = true;
      if (state.filter === 'critical') ok = crit > 0;
      else if (state.filter === 'warning') ok = warn > 0;
      else if (state.filter === 'healthy') ok = crit === 0 && warn === 0;
      if (ok && state.q) ok = row.dataset.text.indexOf(state.q) > -1;
      if (ok && state.check) ok = row.dataset.checks.indexOf(state.check + '|') > -1;
      row.hidden = !ok;
      if (ok) n++;
    });
    shown.textContent = '(' + n + ' of ' + rows.length + (state.check ? ', issue: ' + state.check : '') + ')';
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      state.filter = chip.dataset.filter;
      state.check = '';
      chips.forEach(function (c) { c.classList.toggle('is-active', c === chip); });
      apply();
    });
  });
  if (search) search.addEventListener('input', function () { state.q = search.value.trim().toLowerCase(); apply(); });

  root.querySelectorAll('[data-filter-check]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      state.check = btn.dataset.filterCheck;
      state.filter = 'all';
      chips.forEach(function (c) { c.classList.toggle('is-active', c.dataset.filter === 'all'); });
      apply();
      root.querySelector('.sd-pages').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  root.addEventListener('click', function (e) {
    var btn = e.target.closest('.sd-expand');
    if (!btn) return;
    var detail = btn.closest('tbody').querySelector('.sd-detail');
    var open = detail.hidden;
    detail.hidden = !open;
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.textContent = open ? 'Hide' : 'Details';
  });

  var run = document.getElementById('sdRun');
  if (run) run.closest('form').addEventListener('submit', function () {
    run.disabled = true;
    run.textContent = 'Auditing…';
  });

  apply();
})();
