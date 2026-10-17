/* ProjectsHub — Live Chat inbox (admin). Short-polling client for /admin/api/chat/* */
(function () {
  'use strict';
  var root = document.getElementById('liveChat');
  if (!root) return;
  var $ = function (id) { return document.getElementById(id); };
  var state = {
    filter: 'open', q: '', convs: [], counts: {}, activeId: null, lastId: 0,
    messages: [], conv: null, available: root.dataset.available === '1',
    unreadPrev: null, typingSentAt: 0
  };

  // ── helpers ─────────────────────────────────────────────────
  function csrf() {
    var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }
  function api(url, body) {
    var init = { credentials: 'same-origin', headers: { 'X-Requested-With': 'XMLHttpRequest' } };
    if (body) {
      init.method = 'POST';
      init.headers['Content-Type'] = 'application/json';
      init.headers['X-CSRFToken'] = csrf();
      init.body = JSON.stringify(body);
    }
    return fetch(url, init).then(function (r) {
      if (r.status === 403 && r.redirected) { window.location.reload(); }
      return r.json().catch(function () { return { success: false, error: 'HTTP ' + r.status }; });
    });
  }
  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; }
  function linkify(s) {
    return esc(s)
      .replace(/(https?:\/\/[^\s<]+[^\s<.,;:!?)])/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>')
      .replace(/(^|\s)(\/[a-z0-9][a-z0-9\-\/]*\/?)(?=\s|$|[.,!?])/gi, '$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>');
  }
  function timeAgo(iso) {
    var d = new Date(iso), s = (Date.now() - d.getTime()) / 1000;
    if (s < 60) return 'now';
    if (s < 3600) return Math.floor(s / 60) + 'm';
    if (s < 86400) return Math.floor(s / 3600) + 'h';
    return d.toLocaleDateString([], { day: 'numeric', month: 'short' });
  }
  function clock(iso) { return new Date(iso).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }); }
  function dayLabel(iso) {
    var d = new Date(iso), t = new Date();
    if (d.toDateString() === t.toDateString()) return 'Today';
    var y = new Date(); y.setDate(t.getDate() - 1);
    if (d.toDateString() === y.toDateString()) return 'Yesterday';
    return d.toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short' });
  }
  function uid() { return 'a' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8); }

  // ── availability ────────────────────────────────────────────
  function renderAvailability() {
    $('lcAvailSwitch').setAttribute('aria-checked', state.available ? 'true' : 'false');
    $('lcAvailLabel').textContent = state.available ? 'Available' : 'Away';
    $('lcAvailHint').textContent = state.available
      ? 'Visitors see you online while this page is open'
      : 'Visitors see the team as offline';
    $('lcAwayBanner').classList.toggle('show', !state.available);
  }
  $('lcAvailSwitch').addEventListener('click', function () {
    state.available = !state.available;
    renderAvailability();
    api('/admin/api/chat/presence/', { available: state.available });
    if (state.available) unlockAudio();
  });
  var nameInput = $('lcDisplayName');
  nameInput.value = root.dataset.name || '';
  nameInput.addEventListener('change', function () {
    var v = nameInput.value.trim();
    if (v) api('/admin/api/chat/presence/', { display_name: v });
  });

  // ── alerts ──────────────────────────────────────────────────
  var audioCtx = null;
  function unlockAudio() {
    try { audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)(); if (audioCtx.state === 'suspended') audioCtx.resume(); } catch (e) {}
  }
  document.addEventListener('click', unlockAudio, { once: true });
  function beep() {
    try {
      unlockAudio();
      [0, 0.18].forEach(function (offset) {
        var o = audioCtx.createOscillator(), g = audioCtx.createGain(), t = audioCtx.currentTime + offset;
        o.type = 'sine'; o.frequency.value = 880;
        g.gain.setValueAtTime(0.0001, t);
        g.gain.exponentialRampToValueAtTime(0.18, t + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, t + 0.15);
        o.connect(g); g.connect(audioCtx.destination);
        o.start(t); o.stop(t + 0.16);
      });
    } catch (e) {}
  }
  if ('Notification' in window && Notification.permission === 'default') {
    var nb = $('lcNotifyBtn'); nb.hidden = false;
    nb.addEventListener('click', function () { Notification.requestPermission().then(function () { nb.hidden = true; }); });
  }
  function alertNew(conv) {
    beep();
    if ('Notification' in window && Notification.permission === 'granted' && document.hidden) {
      try {
        var n = new Notification('Live chat: ' + conv.name, { body: conv.last_text || 'New message', tag: 'lc-' + conv.id });
        n.onclick = function () { window.focus(); openConversation(conv.id); n.close(); };
      } catch (e) {}
    }
  }
  var baseTitle = document.title;
  function updateTitle() {
    var unread = state.convs.reduce(function (a, c) { return a + (c.unread || 0); }, 0);
    var waiting = state.counts.waiting || 0;
    var n = Math.max(unread, waiting);
    document.title = (n ? '(' + n + ') ' : '') + baseTitle;
    var badge = document.getElementById('wpLiveChatCount');
    if (badge) { badge.textContent = waiting; badge.className = 'wp-menu-count ' + (waiting ? 'red' : 'blue'); }
  }

  // ── inbox ───────────────────────────────────────────────────
  document.querySelectorAll('.lc-tab').forEach(function (tab) {
    tab.addEventListener('click', function () {
      state.filter = tab.dataset.filter;
      document.querySelectorAll('.lc-tab').forEach(function (t) { t.setAttribute('aria-selected', t === tab ? 'true' : 'false'); });
      loadInbox();
    });
  });
  var searchTimer;
  $('lcSearch').addEventListener('input', function (e) {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(function () { state.q = e.target.value.trim(); loadInbox(); }, 250);
  });

  function loadInbox() {
    var url = '/admin/api/chat/inbox/?filter=' + encodeURIComponent(state.filter) + '&q=' + encodeURIComponent(state.q);
    return api(url).then(function (data) {
      if (!data.success) return;
      var unreadMap = {};
      data.conversations.forEach(function (c) {
        unreadMap[c.id] = c.unread;
        if (state.unreadPrev) {
          var prev = state.unreadPrev[c.id] || 0;
          var isActiveVisible = c.id === state.activeId && !document.hidden;
          if (c.unread > prev && c.last_sender === 'user' && !isActiveVisible) alertNew(c);
        }
      });
      state.unreadPrev = unreadMap;
      state.convs = data.conversations;
      state.counts = data.counts;
      if (data.me && typeof data.me.available === 'boolean' && data.me.available !== state.available) {
        state.available = data.me.available; renderAvailability();
      }
      var team = data.team || {};
      $('lcTeam').textContent = team.online
        ? 'Online now: ' + team.agents.map(function (a) { return a.name; }).join(', ')
        : 'Nobody online, so visitors get the automated assistant';
      renderList(); updateTitle();
    });
  }

  function renderList() {
    Object.keys(state.counts).forEach(function (k) {
      var el = document.querySelector('[data-count="' + k + '"]');
      if (el) { el.textContent = state.counts[k]; el.classList.toggle('hot', k === 'waiting' && state.counts[k] > 0); }
    });
    var list = $('lcList');
    if (!state.convs.length) {
      list.innerHTML = '<li class="lc-empty">' + (state.filter === 'waiting' ? 'Nobody needs a reply. 🎉' : 'No conversations here yet.') + '</li>';
      return;
    }
    list.innerHTML = state.convs.map(function (c) {
      var pills = [];
      if (c.needs_reply) pills.push('<span class="lc-pill waiting">Needs reply</span>');
      if (c.mode === 'waiting') pills.push('<span class="lc-pill waiting">Asked for a person</span>');
      else if (c.mode === 'human') pills.push('<span class="lc-pill human">' + esc(c.assigned ? c.assigned.name : 'Team') + '</span>');
      else if (!c.needs_reply) pills.push('<span class="lc-pill">Assistant only</span>');
      if (c.status === 'lead') pills.push('<span class="lc-pill lead">Lead</span>');
      if (c.status === 'resolved' || c.status === 'archived') pills.push('<span class="lc-pill">Resolved</span>');
      var who = c.last_sender === 'agent' ? 'Team: ' : (c.last_sender === 'bot' ? 'Assistant: ' : '');
      return '<li class="lc-item' + (c.unread ? ' unread' : '') + '" tabindex="0" data-id="' + c.id + '"' +
        (c.id === state.activeId ? ' aria-current="true"' : '') + '>' +
        '<div class="lc-av" style="background:' + esc(c.color) + '">' + esc(c.initials) +
        '<span class="dot' + (c.visitor_online ? ' on' : '') + '" title="' + (c.visitor_online ? 'On the site now' : 'Offline') + '"></span></div>' +
        '<div class="lc-item-main"><div class="lc-item-top"><span class="lc-item-name">' + esc(c.name) + '</span>' +
        '<span class="lc-item-time">' + timeAgo(c.last_at) + '</span></div>' +
        '<div class="lc-item-last">' + (c.visitor_typing ? '<em>typing…</em>' : esc(who + c.last_text)) + '</div>' +
        '<div class="lc-badges">' + pills.join('') + '</div></div>' +
        (c.unread ? '<span class="lc-unread" aria-label="' + c.unread + ' unread">' + c.unread + '</span>' : '') + '</li>';
    }).join('');
  }
  $('lcList').addEventListener('click', function (e) {
    var li = e.target.closest('.lc-item'); if (li) openConversation(parseInt(li.dataset.id, 10));
  });
  $('lcList').addEventListener('keydown', function (e) {
    var li = e.target.closest('.lc-item');
    if (li && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); openConversation(parseInt(li.dataset.id, 10)); }
  });

  // ── thread ──────────────────────────────────────────────────
  function openConversation(id) {
    if (!id) return;
    state.activeId = id; state.lastId = 0; state.messages = []; state.conv = null;
    $('lcPlaceholder').hidden = true; $('lcThread').hidden = false;
    $('lcMsgs').innerHTML = '';
    try { history.replaceState(null, '', '?c=' + id); } catch (e) {}
    renderList();
    loadThread(true).then(function () { $('lcInput').focus(); });
  }

  function loadThread(forceScroll) {
    var id = state.activeId; if (!id) return Promise.resolve();
    return api('/admin/api/chat/' + id + '/messages/?after=' + state.lastId).then(function (data) {
      if (!data.success || id !== state.activeId) return;
      state.conv = data.conversation;
      var fresh = [];
      data.messages.forEach(function (m) {
        var idx = -1;
        for (var i = 0; i < state.messages.length; i++) {
          var x = state.messages[i];
          if (x.id === m.id || (x.client_id && m.client_id && x.client_id === m.client_id)) { idx = i; break; }
        }
        if (idx > -1) state.messages[idx] = m; else { state.messages.push(m); fresh.push(m); }
        state.lastId = Math.max(state.lastId, m.id);
      });
      // Keep server order (by id); unsent optimistic messages stay at the end.
      state.messages.sort(function (a, b) {
        if (a.id && b.id) return a.id - b.id;
        if (!a.id && !b.id) return 0;
        return a.id ? -1 : 1;
      });
      var box = $('lcMsgs');
      var nearBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 140;
      renderThread();
      if (forceScroll || nearBottom) box.scrollTop = box.scrollHeight;
      var c = state.convs.find(function (x) { return x.id === id; });
      if (c && c.unread) { c.unread = 0; renderList(); updateTitle(); }
    });
  }

  function renderThread() {
    var c = state.conv; if (!c) return;
    var av = $('lcThreadAv');
    av.style.background = c.color;
    av.innerHTML = esc(c.initials) + '<span class="dot' + (c.visitor_online ? ' on' : '') + '"></span>';
    $('lcThreadTitle').textContent = c.name;
    var sub = [];
    sub.push(c.visitor_online ? '🟢 On the site now' : (c.visitor_last_seen ? 'Last seen ' + timeAgo(c.visitor_last_seen) + ' ago' : 'Offline'));
    if (c.needs_reply) sub.push('Needs a reply');
    if (c.mode === 'human' && c.assigned) sub.push('Handled by ' + c.assigned.name);
    $('lcThreadSub').textContent = sub.join(' · ');
    $('lcResolveBtn').textContent = (c.status === 'resolved' || c.status === 'archived') ? 'Reopen' : 'Resolve';
    $('lcTyping').textContent = c.visitor_typing ? c.name + ' is typing…' : '';

    var html = [], lastDay = '', prev = null, lastAgentIdx = -1;
    state.messages.forEach(function (m, i) { if (m.sender === 'agent' && m.id) lastAgentIdx = i; });
    state.messages.forEach(function (m, i) {
      var day = dayLabel(m.timestamp);
      if (day !== lastDay) { html.push('<div class="lc-day">' + day + '</div>'); lastDay = day; prev = null; }
      var cont = prev && prev.sender === m.sender && m.sender !== 'system' &&
        (!(m.agent && prev.agent) || m.agent.id === prev.agent.id);
      var who = '';
      if (!cont) {
        if (m.sender === 'user') who = esc(c.name);
        else if (m.sender === 'agent') who = esc(m.agent ? m.agent.name : 'Team');
        else if (m.sender === 'bot') who = 'Automated assistant';
      }
      var meta = m.pending ? 'Sending…' : (m.failed ? 'Not sent. Click to retry' : clock(m.timestamp));
      if (i === lastAgentIdx && (c.visitor_last_read_id || 0) >= m.id) meta += ' · Seen';
      html.push('<div class="lc-row ' + esc(m.sender) + (cont ? ' cont' : '') + (m.pending ? ' pending' : '') + (m.failed ? ' failed' : '') + '"' +
        (m.failed ? ' data-retry="' + esc(m.client_id) + '" role="button" tabindex="0"' : '') + '>' +
        (who ? '<div class="lc-who">' + who + '</div>' : '') +
        '<div class="lc-bubble">' + linkify(m.text) + '</div>' +
        (m.sender !== 'system' ? '<div class="lc-meta">' + meta + '</div>' : '') + '</div>');
      prev = m;
    });
    $('lcMsgs').innerHTML = html.join('');
    renderInfo();
  }

  var infoFor = null;
  function renderInfo() {
    var c = state.conv; if (!c) return;
    var notesEl = $('lcNotes');
    var key = [c.id, c.name, c.email, c.phone, c.page_url, c.mine, c.status].join('|');
    if (infoFor === key && notesEl) return;   // don't clobber notes while typing
    infoFor = key;
    var page = c.page_url ? '<a href="' + esc(c.page_url) + '" target="_blank" rel="noopener">' + esc(c.page_url) + '</a>' : '—';
    var wa = c.phone ? String(c.phone).replace(/\D/g, '') : '';
    $('lcInfo').innerHTML =
      '<h3>Visitor</h3>' +
      '<div class="lc-field"><span>Name</span>' + esc(c.name) + '</div>' +
      '<div class="lc-field"><span>Email</span>' + (c.email ? '<a href="mailto:' + esc(c.email) + '">' + esc(c.email) + '</a>' : '—') + '</div>' +
      '<div class="lc-field"><span>Phone / WhatsApp</span>' + (c.phone ? '<a href="https://wa.me/' + esc(wa) + '" target="_blank" rel="noopener">' + esc(c.phone) + '</a>' : '—') + '</div>' +
      '<div class="lc-field"><span>Current page</span>' + page + '</div>' +
      '<div class="lc-field"><span>Started</span>' + esc(new Date(c.created_at).toLocaleString()) + '</div>' +
      '<h3>Actions</h3>' +
      (c.mine ? '<button type="button" class="lc-btn" data-act="unassign">↩︎ Hand back to queue</button>'
              : '<button type="button" class="lc-btn" data-act="assign">🙋 Assign to me</button>') +
      (c.status !== 'lead' ? '<button type="button" class="lc-btn" data-act="lead">🎯 Mark as lead</button>' : '') +
      '<a class="lc-btn" href="/admin/core/chatbotconversation/' + c.id + '/change/">🗂 Open full record</a>' +
      '<h3><label for="lcNotes">Internal notes</label></h3><textarea id="lcNotes" placeholder="Only visible to the team">' + esc(c.admin_notes || '') + '</textarea>' +
      '<div class="lc-saved" id="lcNotesSaved" aria-live="polite"></div>';
    $('lcNotes').addEventListener('change', function (e) {
      var val = e.target.value;
      api('/admin/api/chat/' + c.id + '/status/', { admin_notes: val }).then(function (d) {
        if (!d.success) return;
        c.admin_notes = val;
        var s = $('lcNotesSaved'); if (s) { s.textContent = 'Saved'; setTimeout(function () { s.textContent = ''; }, 1500); }
      });
    });
  }
  $('lcInfo').addEventListener('click', function (e) {
    var b = e.target.closest('[data-act]'); if (!b || !state.conv) return;
    var body = {};
    if (b.dataset.act === 'assign') body.assign = 'me';
    if (b.dataset.act === 'unassign') body.assign = 'none';
    if (b.dataset.act === 'lead') body.status = 'lead';
    api('/admin/api/chat/' + state.conv.id + '/status/', body).then(function () { loadThread(); loadInbox(); });
  });
  $('lcResolveBtn').addEventListener('click', function () {
    if (!state.conv) return;
    var resolved = state.conv.status === 'resolved' || state.conv.status === 'archived';
    api('/admin/api/chat/' + state.conv.id + '/status/', { status: resolved ? 'active' : 'resolved' })
      .then(function () { loadThread(); loadInbox(); });
  });

  // ── composer ────────────────────────────────────────────────
  var input = $('lcInput');
  function autosize() { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 160) + 'px'; }
  input.addEventListener('input', function () {
    autosize();
    if (!state.activeId) return;
    var now = Date.now();
    if (input.value.trim() && now - state.typingSentAt > 3000) {
      state.typingSentAt = now;
      api('/admin/api/chat/' + state.activeId + '/typing/', { typing: 1 });
    }
  });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); send(); }
  });
  $('lcCompose').addEventListener('submit', function (e) { e.preventDefault(); send(); });
  $('lcCanned').addEventListener('click', function (e) {
    var b = e.target.closest('button[data-text]'); if (!b) return;
    var c = state.conv;
    var first = c && c.name && !/^Visitor #/.test(c.name) ? ' ' + c.name.split(' ')[0] : '';
    input.value = b.dataset.text.replace('{name}', first);
    autosize(); input.focus();
  });
  function retryFrom(el) {
    var row = el.closest('[data-retry]'); if (!row) return;
    var m = state.messages.find(function (x) { return x.client_id === row.dataset.retry; });
    if (m) { m.failed = false; m.pending = true; renderThread(); postReply(m); }
  }
  $('lcMsgs').addEventListener('click', function (e) { retryFrom(e.target); });
  $('lcMsgs').addEventListener('keydown', function (e) { if (e.key === 'Enter') retryFrom(e.target); });

  function send() {
    var text = input.value.trim();
    if (!text || !state.activeId) return;
    var m = { id: 0, sender: 'agent', text: text, client_id: uid(), pending: true,
              timestamp: new Date().toISOString(), agent: { name: nameInput.value || 'You' } };
    state.messages.push(m);
    input.value = ''; autosize();
    renderThread(); $('lcMsgs').scrollTop = $('lcMsgs').scrollHeight;
    state.typingSentAt = 0;
    postReply(m);
  }
  function postReply(m) {
    var convId = state.activeId;
    api('/admin/api/chat/' + convId + '/reply/', { message: m.text, client_id: m.client_id }).then(function (data) {
      if (convId !== state.activeId) return;
      if (data.success) {
        var idx = state.messages.indexOf(m);
        if (idx > -1) state.messages[idx] = data.message;
        loadThread(true); loadInbox();
      } else { m.pending = false; m.failed = true; renderThread(); }
    }).catch(function () { m.pending = false; m.failed = true; renderThread(); });
  }

  // ── polling ─────────────────────────────────────────────────
  function tickInbox() {
    loadInbox().catch(function () {}).then(function () { setTimeout(tickInbox, document.hidden ? 8000 : 4000); });
  }
  function tickThread() {
    (state.activeId ? loadThread() : Promise.resolve()).catch(function () {})
      .then(function () { setTimeout(tickThread, document.hidden ? 6000 : 2000); });
  }

  renderAvailability();
  tickInbox();
  tickThread();
  var initial = parseInt(root.dataset.initial || '', 10);
  if (initial) openConversation(initial);
})();
