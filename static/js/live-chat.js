/* ═══════════════════════════════════════════════════════════════════════════
   ProjectsHub — Live chat widget
   Visitors chat with real ProjectsHub team members (who reply from /admin/live-chat/).
   While nobody is available, a clearly labelled automated assistant gives quick,
   factual answers and the visitor can leave contact details for a human reply.
   Transport: short polling (works on shared hosting; no websockets needed).
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  if (window.phLiveChat) return;

  var configElement = document.getElementById('ph-live-chat-config');
  var CONFIG = {};
  try { CONFIG = configElement ? JSON.parse(configElement.textContent) : {}; } catch (e) {}
  if (CONFIG.enabled === false) return;
  var WHATSAPP = String(CONFIG.whatsapp_number || '').replace(/\D/g, '');
  var STORE_KEY = 'phc_session_v1';
  var MAX_LEN = 1000;
  var POLL_OPEN = 2500, POLL_CLOSED = 15000, POLL_HIDDEN = 30000, PRESENCE_EVERY = 60000;

  // Drop data from the old scripted bot so it never resurfaces.

  var S = {
    open: false, session: null, messages: [], state: null,
    team: { online: false, agents: [], offline_response_time: 'Within 24 hours' },
    lastId: 0, lastSeenId: 0, unread: 0, pollTimer: null, presenceTimer: null,
    typingSentAt: 0, failures: 0, contactDismissed: false, loaded: false
  };

  // ── utils ────────────────────────────────────────────────────────────────
  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; }
  function linkify(text) {
    var html = esc(text);
    html = html.replace(/(https?:\/\/[^\s<]+[^\s<.,;:!?)])/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    html = html.replace(/(^|\s)(\/[a-z0-9][a-z0-9\-\/]*\/?)(?=\s|$|[.,!?])/gi, '$1<a href="$2">$2</a>');
    return html;
  }
  function uid() { return 'c' + Date.now().toString(36) + Math.random().toString(36).slice(2, 10); }
  function clock(iso) { try { return new Date(iso).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }); } catch (e) { return ''; } }
  function loadSession() {
    try { var v = JSON.parse(localStorage.getItem(STORE_KEY) || 'null'); return v && v.session_id && v.token ? v : null; } catch (e) { return null; }
  }
  function saveSession(s) { try { s ? localStorage.setItem(STORE_KEY, JSON.stringify(s)) : localStorage.removeItem(STORE_KEY); } catch (e) {} }
  function ssGet(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function ssSet(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }

  function request(method, url, body) {
    var init = { method: method, headers: { 'X-Requested-With': 'XMLHttpRequest' }, credentials: 'same-origin' };
    if (body) { init.headers['Content-Type'] = 'application/json'; init.body = JSON.stringify(body); }
    return fetch(url, init).then(function (r) {
      return r.json().catch(function () { return { success: false, error: 'Unexpected response' }; })
        .then(function (data) { data._status = r.status; return data; });
    });
  }
  function creds(extra) {
    var o = { session_id: S.session && S.session.session_id, token: S.session && S.session.token };
    for (var k in extra || {}) o[k] = extra[k];
    return o;
  }
  function qs(o) { return Object.keys(o).map(function (k) { return encodeURIComponent(k) + '=' + encodeURIComponent(o[k] == null ? '' : o[k]); }).join('&'); }

  // ── markup ───────────────────────────────────────────────────────────────
  var ICON_CHAT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v8a2.5 2.5 0 0 1-2.5 2.5H10l-4.2 3.6c-.5.4-1.3.1-1.3-.6V16A2.5 2.5 0 0 1 4 13.5z" fill="currentColor"/></svg>';
  var ICON_CLOSE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>';
  var ICON_DOWN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var ICON_SEND = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12l15-7-5.5 15-2.5-6.5z" fill="currentColor"/></svg>';
  var ICON_WA = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3z"/></svg>';
  var ICON_BOT = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="8" width="16" height="11" rx="3" fill="currentColor" opacity=".9"/><circle cx="9.5" cy="13.5" r="1.4" fill="#fff"/><circle cx="14.5" cy="13.5" r="1.4" fill="#fff"/><path d="M12 4v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';

  function attrEsc(s) {
    return esc(s).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function suggestedButtonsMarkup() {
    return (Array.isArray(CONFIG.suggested_buttons) ? CONFIG.suggested_buttons : []).map(function (button) {
      return '<button type="button" data-q="' + attrEsc(button.prompt) + '" data-action="' + attrEsc(button.kind) + '">' + esc(button.label) + '</button>';
    }).join('');
  }

  function build() {
    var wrap = document.createElement('div');
    wrap.className = 'phc';
    wrap.id = 'phChat';
    var whatsappLink = WHATSAPP
      ? '<a class="phc-icon-btn phc-wa" href="https://wa.me/' + encodeURIComponent(WHATSAPP) + '?text=' + encodeURIComponent(CONFIG.whatsapp_message || '') + '" target="_blank" rel="noopener noreferrer" aria-label="Continue on WhatsApp" title="Continue on WhatsApp">' + ICON_WA + '</a>'
      : '';
    wrap.innerHTML =
      '<div class="phc-teaser" id="phcTeaser" hidden>' +
        '<button type="button" class="phc-teaser-close" aria-label="Dismiss">' + ICON_CLOSE + '</button>' +
        '<button type="button" class="phc-teaser-body" id="phcTeaserOpen">' +
          '<span class="phc-avatars" id="phcTeaserAvatars"></span>' +
          '<span class="phc-teaser-text" id="phcTeaserText"></span>' +
        '</button>' +
      '</div>' +
      '<div class="phc-panel" id="phcPanel" role="dialog" aria-modal="false" aria-labelledby="phcTitle" hidden>' +
        '<div class="phc-head">' +
          '<span class="phc-avatars" id="phcHeadAvatars"></span>' +
          '<div class="phc-head-text">' +
            '<h2 class="phc-title" id="phcTitle">' + esc(CONFIG.team_name || 'ProjectsHub team') + '</h2>' +
            '<p class="phc-status" id="phcStatus"><span class="phc-dot"></span><span id="phcStatusText">Checking who is online…</span></p>' +
          '</div>' +
          whatsappLink +
          '<button type="button" class="phc-icon-btn" id="phcMinimize" aria-label="Minimise chat" title="Minimise">' + ICON_DOWN + '</button>' +
        '</div>' +
        '<div class="phc-body" id="phcBody">' +
          '<div class="phc-intro" id="phcIntro"></div>' +
          '<div class="phc-session-notice" id="phcSessionNotice" role="status" aria-live="polite" hidden></div>' +
          '<div class="phc-log" id="phcLog" role="log" aria-live="polite" aria-relevant="additions"></div>' +
          '<div class="phc-typing" id="phcTyping" hidden><span class="phc-typing-dots"><i></i><i></i><i></i></span><span id="phcTypingText"></span></div>' +
          '<form class="phc-contact" id="phcContact" hidden novalidate>' +
            '<p class="phc-contact-title">Want a person to follow up?</p>' +
            '<p class="phc-contact-sub">' + esc((CONFIG.contact_followup || '').replace(/\{response_time\}/g, CONFIG.response_time || 'Within 24 hours')) + '</p>' +
            '<label class="phc-field"><span>Name</span><input name="name" type="text" autocomplete="name" maxlength="150" placeholder="Your name"></label>' +
            '<label class="phc-field"><span>Email</span><input name="email" type="email" autocomplete="email" maxlength="254" placeholder="you@example.com"></label>' +
            '<label class="phc-field"><span>WhatsApp / phone <em>(optional)</em></span><input name="phone" type="tel" autocomplete="tel" maxlength="25" placeholder="+91 …"></label>' +
            '<p class="phc-contact-error" id="phcContactError" role="alert"></p>' +
            '<div class="phc-contact-actions"><button type="submit" class="phc-btn">Save details</button><button type="button" class="phc-link" id="phcContactSkip">Not now</button></div>' +
          '</form>' +
        '</div>' +
        '<div class="phc-quick" id="phcQuick" role="group" aria-label="' + attrEsc(CONFIG.suggested_buttons_heading || 'Quick reply buttons') + '">' +
          '<span class="phc-quick-label">' + esc(CONFIG.suggested_buttons_heading || '') + '</span>' +
          suggestedButtonsMarkup() +
        '</div>' +
        '<form class="phc-composer" id="phcComposer" autocomplete="off">' +
          '<label class="phc-sr" for="phcInput">Message</label>' +
          '<textarea id="phcInput" rows="1" maxlength="' + MAX_LEN + '" placeholder="Type your message…" enterkeyhint="send"></textarea>' +
          '<button type="submit" class="phc-send" id="phcSend" aria-label="Send message" disabled>' + ICON_SEND + '</button>' +
        '</form>' +
        '<p class="phc-foot"><span id="phcCounter" class="phc-counter"></span>Real people reply here · automated answers are labelled</p>' +
      '</div>' +
      '<button type="button" class="phc-launcher" id="phcLauncher" aria-controls="phcPanel" aria-expanded="false" aria-label="Chat with ' + esc(CONFIG.team_name || 'the ProjectsHub team') + '">' +
        '<span class="phc-launcher-icon phc-launcher-icon--chat">' + ICON_CHAT + '</span>' +
        '<span class="phc-launcher-icon phc-launcher-icon--close">' + ICON_CLOSE + '</span>' +
        '<span class="phc-launcher-online" id="phcLauncherOnline" hidden></span>' +
        '<span class="phc-badge" id="phcBadge" hidden>0</span>' +
      '</button>';
    document.body.appendChild(wrap);
  }

  var el = {};
  function cache() {
    ['phChat', 'phcTeaser', 'phcTeaserOpen', 'phcTeaserAvatars', 'phcTeaserText', 'phcPanel', 'phcHeadAvatars', 'phcTitle',
     'phcSessionNotice',
     'phcStatus', 'phcStatusText', 'phcMinimize', 'phcBody', 'phcIntro', 'phcLog', 'phcTyping', 'phcTypingText', 'phcContact',
     'phcContactError', 'phcContactSkip', 'phcQuick', 'phcComposer', 'phcInput', 'phcSend', 'phcCounter', 'phcLauncher',
     'phcLauncherOnline', 'phcBadge'].forEach(function (id) { el[id] = document.getElementById(id); });
  }

  // ── rendering ────────────────────────────────────────────────────────────
  function avatar(a, size) {
    return '<span class="phc-av' + (size ? ' phc-av--' + size : '') + '" style="background:' + esc(a.color || '#4f46e5') + '" aria-hidden="true">' + esc(a.initials || 'PH') + '</span>';
  }
  function teamAvatars(showWordmark) {
    var agent = S.state && S.state.mode === 'human' && S.state.agent;
    if (agent) return avatar(agent);
    if (S.team.agents && S.team.agents.length) return S.team.agents.map(function (a) { return avatar(a); }).join('');
    if (showWordmark) {
      return '<span class="phc-brand-wordmark"><img src="/static/image/logo/projectshub-logo-light.svg" alt="ProjectsHub — Connect, Collaborate, Achieve"></span>';
    }
    return '<span class="phc-av phc-av--brand" aria-hidden="true"><img src="/static/image/Favicon-new/android-chrome-192x192.png" alt=""></span>';
  }

  function renderHeader() {
    var st = S.state || {};
    var agent = st.mode === 'human' && st.agent;
    var online, title, text;
    if (agent) {
      title = agent.name;
      online = !!agent.online;
      text = online
        ? (CONFIG.team_name || 'ProjectsHub team') + ' · Active now'
        : (CONFIG.team_name || 'ProjectsHub team') + ' · Away. We\'ll reply here or by email';
    } else if (S.team.online) {
      title = CONFIG.team_name || 'ProjectsHub team';
      online = true;
      text = 'Online now · usually replies in a few minutes';
    } else {
      title = CONFIG.team_name || 'ProjectsHub team';
      online = false;
      text = 'Away · we reply ' + (S.team.offline_response_time || 'within 24 hours').toLowerCase();
    }
    el.phcTitle.textContent = title;
    el.phcStatusText.textContent = text;
    el.phcStatus.classList.toggle('is-online', online);
    el.phcHeadAvatars.innerHTML = teamAvatars(true);
    el.phcLauncherOnline.hidden = !S.team.online;
    el.phcLauncher.setAttribute('aria-label', 'Chat with ' + (CONFIG.team_name || 'the ProjectsHub team') + (S.team.online ? ' (online now)' : ''));
  }

  function renderIntro() {
    var names = (S.team.agents || []).map(function (a) { return a.name; });
    var who = names.length ? names.slice(0, 2).join(' & ') : '';
    var text = S.team.online
      ? (CONFIG.online_greeting || 'Hi 👋 You\'re chatting with real people at ProjectsHub.') + (who ? ' ' + who + (names.length > 1 ? ' are' : ' is') + ' online.' : '')
      : (CONFIG.offline_greeting || 'Hi 👋 Ask me about our projects, workshops or custom AI work.');
    el.phcIntro.innerHTML = '<div class="phc-intro-card">' + teamAvatars() + '<p>' + esc(text) + '</p></div>';
  }

  function groupKey(m) {
    if (m.sender === 'agent') return 'agent:' + (m.agent ? m.agent.id || m.agent.name : '');
    return m.sender;
  }

  function renderLog(scroll) {
    var nearBottom = el.phcBody.scrollHeight - el.phcBody.scrollTop - el.phcBody.clientHeight < 120;
    var st = S.state || {};
    var lastUserIdx = -1;
    S.messages.forEach(function (m, i) {
      if (m.sender === 'user') lastUserIdx = i;
    });
    el.phcIntro.hidden = lastUserIdx > -1;
    var html = [];
    var lastOfflineSystemHtmlIndex = -1;
    for (var i = 0; i < S.messages.length; i++) {
      var m = S.messages[i], prev = S.messages[i - 1], next = S.messages[i + 1];
      var first = !prev || groupKey(prev) !== groupKey(m);
      var last = !next || groupKey(next) !== groupKey(m);
      if (m.sender === 'system') {
        var systemHtml = '<div class="phc-sys">' + linkify(m.text) + '</div>';
        if (/team is offline/i.test(m.text) && lastOfflineSystemHtmlIndex > -1) {
          html[lastOfflineSystemHtmlIndex] = systemHtml;
          continue;
        }
        html.push(systemHtml);
        lastOfflineSystemHtmlIndex = /team is offline/i.test(m.text) ? html.length - 1 : -1;
        continue;
      }
      lastOfflineSystemHtmlIndex = -1;
      var cls = 'phc-msg phc-msg--' + m.sender + (first ? ' is-first' : '') + (last ? ' is-last' : '') +
        (m._pending ? ' is-pending' : '') + (m._failed ? ' is-failed' : '');
      var side = m.sender === 'user' ? '' :
        '<span class="phc-msg-av">' + (last ? (m.sender === 'bot'
          ? '<span class="phc-av phc-av--bot" aria-hidden="true">' + ICON_BOT + '</span>'
          : avatar(m.agent || {})) : '') + '</span>';
      var label = '';
      if (first && m.sender === 'agent') label = '<span class="phc-msg-name">' + esc(m.agent ? m.agent.name : 'ProjectsHub team') + '<span class="phc-msg-role"> · ProjectsHub team</span></span>';
      if (first && m.sender === 'bot') label = '<span class="phc-msg-name">Assistant <span class="phc-tag">Automated</span></span>';
      var meta = '';
      if (m.sender === 'user' && last) {
        if (m._failed) meta = '<button type="button" class="phc-retry" data-retry="' + esc(m.client_id) + '">Not sent · Tap to retry</button>';
        else if (m._pending) meta = '<span class="phc-meta">Sending…</span>';
        else if (i === lastUserIdx && st.last_read_by_team >= m.id && (st.mode === 'human')) meta = '<span class="phc-meta">Seen · ' + clock(m.timestamp) + '</span>';
        else meta = '<span class="phc-meta">' + clock(m.timestamp) + '</span>';
      } else if (last) {
        meta = '<span class="phc-meta">' + clock(m.timestamp) + '</span>';
      }
      html.push('<div class="' + cls + '">' + side + '<div class="phc-msg-main">' + label +
        '<div class="phc-bubble">' + linkify(m.text) + '</div>' + meta + '</div></div>');
    }
    el.phcLog.innerHTML = html.join('');
    renderTyping();
    renderContact();
    renderQuick();
    if (scroll || nearBottom) scrollBottom();
  }

  function renderTyping() {
    var st = S.state || {};
    var show = !!st.agent_typing;
    el.phcTyping.hidden = !show;
    el.phcTypingText.textContent = show ? (st.agent_typing_name || (st.agent && st.agent.name) || 'The team') + ' is typing…' : '';
  }

  function renderQuick() {
    var visibleCount = 0;
    el.phcQuick.querySelectorAll('button[data-action]').forEach(function (button) {
      button.hidden = false;
      visibleCount += 1;
    });
    el.phcQuick.hidden = visibleCount === 0;
  }

  function renderContact() {
    var st = S.state || {};
    var hasUserMsg = S.messages.some(function (m) { return m.sender === 'user' && !m._pending; });
    var agentActive = st.mode === 'human' && st.agent && st.agent.online;
    // Ask for contact details only when a live reply isn't imminent: team offline, the wait is
    // running long, or the team member handling the chat has gone away.
    var replyUnlikelySoon = !S.team.online || st.followup_prompted || (st.mode === 'human' && st.agent && !st.agent.online);
    var show = !!(S.session && hasUserMsg && !st.has_contact && !S.contactDismissed && !agentActive && replyUnlikelySoon);
    el.phcContact.hidden = !show;
  }

  function scrollBottom() {
    requestAnimationFrame(function () { el.phcBody.scrollTop = el.phcBody.scrollHeight; });
  }

  function renderBadge() {
    el.phcBadge.hidden = !S.unread;
    el.phcBadge.textContent = S.unread > 9 ? '9+' : String(S.unread);
  }

  // ── message state ────────────────────────────────────────────────────────
  function mergeMessages(list) {
    var added = 0;
    (list || []).forEach(function (m) {
      var idx = -1;
      for (var i = 0; i < S.messages.length; i++) {
        var x = S.messages[i];
        if ((x.id && x.id === m.id) || (m.client_id && x.client_id === m.client_id)) { idx = i; break; }
      }
      if (idx > -1) S.messages[idx] = m;
      else { S.messages.push(m); added++; if (m.sender !== 'user' && !S.open && m.id > S.lastSeenId) S.unread++; }
      if (m.id) S.lastId = Math.max(S.lastId, m.id);
    });
    S.messages.sort(function (a, b) {
      if (a.id && b.id) return a.id - b.id;
      if (!a.id && !b.id) return 0;
      return a.id ? -1 : 1;   // pending (no id yet) stay at the end
    });
    return added;
  }

  function applyState(st) {
    if (!st) return;
    S.state = st;
    renderHeader();
  }

  // ── network ──────────────────────────────────────────────────────────────
  function resetSession(notice) {
    S.session = null; saveSession(null);
    S.messages = S.messages.filter(function (m) { return m._pending || m._failed; });
    S.state = null; S.lastId = 0;
    S.lastSeenId = 0; S.unread = 0; S.contactDismissed = false;
    ssSet('phc_seen', '0');
    ssSet('phc_contact_skip', '');
    if (el.phcContact) el.phcContact.reset();
    if (el.phcInput) {
      el.phcInput.value = '';
      autosize();
      updateComposer();
    }
    if (el.phcSessionNotice) {
      el.phcSessionNotice.textContent = notice || 'Your previous chat session is no longer available. Choose a topic below or send a message to start a new conversation.';
      el.phcSessionNotice.hidden = false;
    }
    renderBadge();
  }

  function handleExpiredSession(data) {
    if (!data || data._status !== 403 || !data.reset) return false;
    resetSession();
    renderIntro();
    renderLog(true);
    schedule();
    return true;
  }

  function clearSessionNotice() {
    if (!el.phcSessionNotice) return;
    el.phcSessionNotice.textContent = '';
    el.phcSessionNotice.hidden = true;
  }

  function fetchPresence() {
    return request('GET', '/api/chat/presence/').then(function (d) {
      if (d.success && d.team) { S.team = d.team; renderHeader(); if (!S.session || !S.messages.length) renderIntro(); updateTeaser(); }
    }).catch(function () {});
  }

  function resume() {
    if (!S.session) { S.loaded = true; return Promise.resolve(); }
    return request('POST', '/api/chat/session/', creds()).then(function (d) {
      if (d.team) S.team = d.team;
      if (!d.success || !d.session) {
        resetSession('Your previous chat session timed out or could not be restored. Choose a topic below or send a message to start again.');
      }
      else {
        S.messages = [];
        mergeMessages(d.messages);
        applyState(d.state);
        S.lastSeenId = parseInt(ssGet('phc_seen') || '0', 10) || 0;
        S.unread = S.messages.filter(function (m) { return m.sender !== 'user' && m.sender !== 'system' && m.id > S.lastSeenId; }).length;
      }
      S.loaded = true;
      renderHeader(); renderIntro(); renderLog(true); renderBadge();
    }).catch(function () { S.loaded = true; });
  }

  function poll() {
    clearTimeout(S.pollTimer);
    if (!S.session) { schedule(); return; }
    var q = qs(creds({ after: S.lastId, read: S.open && !document.hidden ? 1 : 0 }));
    request('GET', '/api/chat/poll/?' + q).then(function (d) {
      if (handleExpiredSession(d)) return;
      if (!d.success) throw new Error(d.error || 'poll failed');
      S.failures = 0;
      if (d.team) S.team = d.team;
      var added = mergeMessages(d.messages);
      applyState(d.state);
      if (S.open) markSeen();
      if (added || S.open) renderLog();
      renderBadge();
      if (added && !S.open) nudge();
      schedule();
    }).catch(function () { S.failures++; schedule(); });
  }

  function schedule() {
    clearTimeout(S.pollTimer);
    if (!S.session) return;
    var base = document.hidden ? POLL_HIDDEN : (S.open ? POLL_OPEN : POLL_CLOSED);
    var delay = Math.min(base * Math.pow(2, S.failures), 60000);
    S.pollTimer = setTimeout(poll, delay);
  }

  function markSeen() {
    var maxId = 0;
    S.messages.forEach(function (m) { if (m.id > maxId) maxId = m.id; });
    S.lastSeenId = maxId; ssSet('phc_seen', String(maxId));
    S.unread = 0; renderBadge();
  }

  function sendText(text, opts) {
    opts = opts || {};
    text = (text || '').trim();
    if (!text) return Promise.resolve();
    var m = { id: 0, sender: 'user', text: text.slice(0, MAX_LEN), client_id: uid(), timestamp: new Date().toISOString(), _pending: true };
    if (opts.requestHuman) m.requestHuman = true;
    S.messages.push(m);
    renderLog(true);
    return postMessage(m);
  }

  function postMessage(m, isRetry) {
    var body = { message: m.text, client_id: m.client_id, page_url: location.pathname + location.search };
    if (m.requestHuman) body.request_human = true;
    if (S.session) { body.session_id = S.session.session_id; body.token = S.session.token; }
    return request('POST', '/api/chat/message/', body).then(function (d) {
      if (d._status === 403 && d.reset && !isRetry) {
        resetSession();
        return postMessage(m, true);
      }
      if (!d.success) {
        m._pending = false; m._failed = true; m._error = d.error;
        renderLog();
        if (d.error) showSystemLocal(d.error);
        return false;
      }
      if (d.session && d.session.token) { S.session = d.session; saveSession(d.session); }
      clearSessionNotice();
      var idx = S.messages.indexOf(m);
      if (idx > -1) S.messages.splice(idx, 1);
      mergeMessages([d.message].concat(d.replies || []));
      applyState(d.state);
      markSeen();
      renderLog(true);
      schedule();
      return true;
    }).catch(function () {
      m._pending = false; m._failed = true; renderLog();
      return false;
    });
  }

  var localNoticeTimer;
  function showSystemLocal(text) {
    var n = document.createElement('div');
    n.className = 'phc-sys phc-sys--error';
    n.textContent = text;
    el.phcLog.appendChild(n);
    scrollBottom();
    clearTimeout(localNoticeTimer);
    localNoticeTimer = setTimeout(function () { if (n.parentNode) n.parentNode.removeChild(n); }, 6000);
  }

  function sendTyping() {
    if (!S.session) return;
    var now = Date.now();
    if (now - S.typingSentAt < 3000) return;
    S.typingSentAt = now;
    request('POST', '/api/chat/typing/', creds({ typing: 1 })).then(handleExpiredSession).catch(function () {});
  }

  // ── open / close / teaser ────────────────────────────────────────────────
  function setOpen(open) {
    S.open = open;
    el.phcPanel.hidden = !open;
    el.phChat.classList.toggle('is-open', open);
    document.body.classList.toggle('live-chat-open', open);
    el.phcLauncher.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.documentElement.classList.toggle('phc-lock', open && window.matchMedia('(max-width: 520px)').matches);
    if (open) {
      hideTeaser(true);
      markSeen();
      renderIntro(); renderLog(true);
      setTimeout(function () { el.phcInput.focus({ preventScroll: true }); }, 60);
      if (!S.session) fetchPresence();
      poll();
    } else {
      schedule();
    }
  }

  function updateTeaser() {
    if (!el.phcTeaser.hidden) {
      el.phcTeaserAvatars.innerHTML = teamAvatars();
      el.phcTeaserText.textContent = teaserText();
    }
  }
  function teaserText() {
    return S.team.online
      ? 'Hi! We\'re online. Questions about a project or custom AI? Chat with our team.'
      : 'Questions about a project or custom AI? Leave us a message and our team will reply.';
  }
  function showTeaser() {
    if (S.open || ssGet('phc_teaser') === '1' || S.messages.length) return;
    el.phcTeaserAvatars.innerHTML = teamAvatars();
    el.phcTeaserText.textContent = teaserText();
    el.phcTeaser.hidden = false;
    requestAnimationFrame(function () {
      el.phcTeaser.classList.add('is-visible');
      document.body.classList.add('live-chat-teaser-visible');
    });
  }
  function hideTeaser(remember) {
    el.phcTeaser.classList.remove('is-visible');
    el.phcTeaser.hidden = true;
    document.body.classList.remove('live-chat-teaser-visible');
    if (remember) ssSet('phc_teaser', '1');
  }
  var nudgeTimer;
  function nudge() {
    el.phcLauncher.classList.remove('is-nudging');
    void el.phcLauncher.offsetWidth;
    el.phcLauncher.classList.add('is-nudging');
    clearTimeout(nudgeTimer);
    nudgeTimer = setTimeout(function () { el.phcLauncher.classList.remove('is-nudging'); }, 1200);
  }

  // ── events ───────────────────────────────────────────────────────────────
  function autosize() {
    el.phcInput.style.height = 'auto';
    el.phcInput.style.height = Math.min(el.phcInput.scrollHeight, 120) + 'px';
  }
  function updateComposer() {
    var len = el.phcInput.value.length;
    el.phcSend.disabled = !el.phcInput.value.trim();
    el.phcCounter.textContent = len > MAX_LEN - 150 ? (MAX_LEN - len) + ' characters left · ' : '';
  }

  function bind() {
    el.phcLauncher.addEventListener('click', function () { setOpen(!S.open); if (!S.open) el.phcLauncher.focus(); });
    el.phcMinimize.addEventListener('click', function () { setOpen(false); el.phcLauncher.focus(); });
    el.phcTeaserOpen.addEventListener('click', function () { setOpen(true); });
    el.phcTeaser.querySelector('.phc-teaser-close').addEventListener('click', function () { hideTeaser(true); });

    // Dismiss the proactive teaser on scroll so it never blocks page content
    // (e.g. footer social buttons) once the user begins interacting with the page.
    var teaserHiddenOnScroll = false;
    window.addEventListener('scroll', function () {
      if (!teaserHiddenOnScroll && !el.phcTeaser.hidden) { teaserHiddenOnScroll = true; hideTeaser(false); }
    }, { passive: true });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && S.open && el.phChat.contains(document.activeElement)) { setOpen(false); el.phcLauncher.focus(); }
    });

    el.phcComposer.addEventListener('submit', function (e) {
      e.preventDefault();
      var text = el.phcInput.value;
      if (!text.trim()) return;
      el.phcInput.value = ''; autosize(); updateComposer();
      sendText(text);
      el.phcInput.focus();
    });
    el.phcInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); el.phcComposer.requestSubmit ? el.phcComposer.requestSubmit() : el.phcComposer.dispatchEvent(new Event('submit', { cancelable: true })); }
    });
    el.phcInput.addEventListener('input', function () { autosize(); updateComposer(); if (el.phcInput.value.trim()) sendTyping(); });

    el.phcQuick.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      if (b.dataset.action === 'handoff') sendText(b.dataset.q, { requestHuman: true });
      else sendText(b.dataset.q);
    });

    el.phcLog.addEventListener('click', function (e) {
      var r = e.target.closest('[data-retry]'); if (!r) return;
      var m = S.messages.find(function (x) { return x.client_id === r.dataset.retry; });
      if (m) { m._failed = false; m._pending = true; renderLog(); postMessage(m); }
    });

    el.phcContactSkip.addEventListener('click', function () { S.contactDismissed = true; ssSet('phc_contact_skip', '1'); renderContact(); });
    el.phcContact.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = el.phcContact, btn = f.querySelector('button[type="submit"]');
      var fe = f.elements;
      var data = { name: fe['name'].value.trim(), email: fe['email'].value.trim(), phone: fe['phone'].value.trim() };
      el.phcContactError.textContent = '';
      if (!data.email && !data.phone) { el.phcContactError.textContent = 'Please add your email or WhatsApp number.'; fe['email'].focus(); return; }
      if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) { el.phcContactError.textContent = 'Please check your email address.'; fe['email'].focus(); return; }
      btn.disabled = true; btn.textContent = 'Saving…';
      request('POST', '/api/chat/profile/', creds(data)).then(function (d) {
        btn.disabled = false; btn.textContent = 'Save details';
        if (handleExpiredSession(d)) return;
        if (!d.success) { el.phcContactError.textContent = d.error || 'Could not save. Please try again.'; return; }
        mergeMessages(d.replies); applyState(d.state); markSeen(); renderLog(true);
      }).catch(function () { btn.disabled = false; btn.textContent = 'Save details'; el.phcContactError.textContent = 'Network error. Please try again.'; });
    });

    document.addEventListener('visibilitychange', function () {
      if (!document.hidden && S.session) poll();
      else schedule();
    });
    window.addEventListener('online', function () { S.failures = 0; poll(); });
  }

  // ── boot ─────────────────────────────────────────────────────────────────
  function boot() {
    build(); cache(); bind();
    S.session = loadSession();
    S.contactDismissed = ssGet('phc_contact_skip') === '1';
    renderHeader(); renderIntro(); renderQuick();
    fetchPresence().then(resume).then(function () {
      schedule();
      if (/[?&]chat=open\b/.test(location.search)) setOpen(true);
      else setTimeout(showTeaser, 9000);
    });
    S.presenceTimer = setInterval(function () { if (!document.hidden && !S.session) fetchPresence(); }, PRESENCE_EVERY);
  }

  window.phLiveChat = {
    open: function () { setOpen(true); },
    close: function () { setOpen(false); },
    send: function (t) { setOpen(true); return sendText(t); }
  };
  // Backwards compatibility with old inline handlers (window.chatbot.*)
  window.chatbot = { toggleChat: function (f) { setOpen(typeof f === 'boolean' ? f : !S.open); } };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
