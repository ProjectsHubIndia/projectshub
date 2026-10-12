/**
 * ProjectsHub — Cookie Consent & Privacy Preference Engine
 * GDPR, CCPA & ePrivacy Directive Compliant
 * Zero Dependencies | Vanilla JS | < 3KB
 */
(function (window, document) {
  'use strict';

  var STORAGE_KEY = 'ph_cookie_consent_v1';
  var COOKIE_NAME = 'ph_cookie_consent';
  var COOKIE_MAX_AGE_DAYS = 365;

  var state = {
    necessary: true,
    analytics: false,
    marketing: false,
    timestamp: null,
    version: 1
  };

  /**
   * Helper: Read browser cookie
   */
  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^|;\\s*)(' + name + ')=([^;]*)'));
    return match ? decodeURIComponent(match[3]) : null;
  }

  /**
   * Helper: Set browser cookie
   */
  function setCookie(name, value, days) {
    var expires = '';
    if (days) {
      var d = new Date();
      d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = '; expires=' + d.toUTCString();
    }
    var secure = window.location.protocol === 'https:' ? '; Secure' : '';
    document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/; SameSite=Lax' + secure;
  }

  /**
   * Load stored consent from localStorage or Cookie fallback
   */
  function loadConsent() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        raw = getCookie(COOKIE_NAME);
      }
      if (raw) {
        var parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object' && parsed.version === 1) {
          state.necessary = true;
          state.analytics = Boolean(parsed.analytics);
          state.marketing = Boolean(parsed.marketing);
          state.timestamp = parsed.timestamp;
          return true;
        }
      }
    } catch (e) {
      // Local storage disabled or corrupted
    }
    return false;
  }

  /**
   * Persist current state to localStorage and Cookie
   */
  function persistConsent() {
    state.timestamp = Date.now();
    var payload = JSON.stringify(state);
    try {
      localStorage.setItem(STORAGE_KEY, payload);
    } catch (e) {}
    setCookie(COOKIE_NAME, payload, COOKIE_MAX_AGE_DAYS);

    // Apply analytics preferences
    applyAnalyticsState();

    // Broadcast event for external scripts/tags
    window.dispatchEvent(new CustomEvent('ph:cookieConsentUpdated', {
      detail: Object.assign({}, state)
    }));
  }

  /**
   * Enable/Disable Google Analytics based on user consent
   */
  function applyAnalyticsState() {
    var gaId = window.__PH_GA_ID__;
    if (gaId) {
      if (state.analytics) {
        window['ga-disable-' + gaId] = false;
        if (typeof window.__phLoadGtag === 'function') {
          window.__phLoadGtag();
        }
      } else {
        window['ga-disable-' + gaId] = true;
      }
    }
  }

  /**
   * DOM Elements & Banner Controller
   */
  var elements = {};

  function cacheElements() {
    elements.banner = document.getElementById('cookieConsentBanner');
    elements.closeBtn = document.getElementById('cookieCloseBtn');
    elements.acceptAllBtn = document.getElementById('cookieAcceptAllBtn');
    elements.rejectBtn = document.getElementById('cookieRejectBtn');
    elements.prefsToggleBtn = document.getElementById('cookiePrefsToggleBtn');
    elements.saveCustomBtn = document.getElementById('cookieSaveCustomBtn');
    elements.prefsPanel = document.getElementById('cookiePrefsPanel');
    elements.catAnalytics = document.getElementById('cookieCatAnalytics');
    elements.catMarketing = document.getElementById('cookieCatMarketing');
  }

  function showBanner() {
    if (!elements.banner) return;
    elements.banner.style.display = 'block';
    elements.banner.setAttribute('aria-hidden', 'false');
    // Micro-delay for smooth CSS entrance transition
    requestAnimationFrame(function () {
      elements.banner.classList.add('ph-cookie-visible');
    });
  }

  function hideBanner() {
    if (!elements.banner) return;
    elements.banner.classList.remove('ph-cookie-visible');
    setTimeout(function () {
      elements.banner.style.display = 'none';
      elements.banner.setAttribute('aria-hidden', 'true');
    }, 350);
  }

  function togglePreferences(show) {
    if (!elements.prefsPanel) return;
    var isExpanded = show !== undefined ? show : elements.prefsPanel.style.display === 'none';

    elements.prefsPanel.style.display = isExpanded ? 'block' : 'none';
    elements.prefsPanel.setAttribute('aria-hidden', !isExpanded);

    if (elements.prefsToggleBtn) {
      elements.prefsToggleBtn.setAttribute('aria-expanded', isExpanded);
      var textDef = elements.prefsToggleBtn.querySelector('.prefs-text-default');
      var textAct = elements.prefsToggleBtn.querySelector('.prefs-text-active');
      if (textDef && textAct) {
        textDef.style.display = isExpanded ? 'none' : 'inline';
        textAct.style.display = isExpanded ? 'inline' : 'none';
      }
    }

    if (elements.saveCustomBtn) {
      elements.saveCustomBtn.style.display = isExpanded ? 'inline-flex' : 'none';
    }
  }

  function updateCheckboxesFromState() {
    if (elements.catAnalytics) {
      elements.catAnalytics.checked = Boolean(state.analytics);
    }
    if (elements.catMarketing) {
      elements.catMarketing.checked = Boolean(state.marketing);
    }
  }

  function acceptAll() {
    state.analytics = true;
    state.marketing = true;
    persistConsent();
    hideBanner();
  }

  function rejectAll() {
    state.analytics = false;
    state.marketing = false;
    persistConsent();
    hideBanner();
  }

  function savePreferences() {
    state.analytics = elements.catAnalytics ? elements.catAnalytics.checked : false;
    state.marketing = elements.catMarketing ? elements.catMarketing.checked : false;
    persistConsent();
    hideBanner();
  }

  function openPreferences() {
    cacheElements();
    updateCheckboxesFromState();
    showBanner();
    togglePreferences(true);
  }

  function init() {
    cacheElements();
    var hasStored = loadConsent();

    // Setup initial analytics gating
    applyAnalyticsState();

    if (!hasStored) {
      // Delay banner display by 700ms so initial page render and core metrics complete first
      setTimeout(showBanner, 700);
    } else {
      updateCheckboxesFromState();
    }

    // Attach event listeners
    if (elements.acceptAllBtn) {
      elements.acceptAllBtn.addEventListener('click', acceptAll);
    }
    if (elements.rejectBtn) {
      elements.rejectBtn.addEventListener('click', rejectAll);
    }
    if (elements.prefsToggleBtn) {
      elements.prefsToggleBtn.addEventListener('click', function () {
        togglePreferences();
      });
    }
    if (elements.saveCustomBtn) {
      elements.saveCustomBtn.addEventListener('click', savePreferences);
    }
    if (elements.closeBtn) {
      elements.closeBtn.addEventListener('click', function () {
        // If user closes with 'x' without choice, treat as reject non-essential or dismiss
        rejectAll();
      });
    }

    // Accessibility: close on Escape if banner is visible
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && elements.banner && elements.banner.classList.contains('ph-cookie-visible')) {
        hideBanner();
      }
    });
  }

  // Public API
  window.ProjectsHubCookieConsent = {
    init: init,
    acceptAll: acceptAll,
    rejectAll: rejectAll,
    savePreferences: savePreferences,
    openPreferences: openPreferences,
    hasConsent: function () {
      return state.timestamp !== null;
    },
    allowsAnalytics: function () {
      return Boolean(state.analytics);
    },
    allowsMarketing: function () {
      return Boolean(state.marketing);
    },
    getConsent: function () {
      return Object.assign({}, state);
    }
  };

  // Auto-init on DOM readiness
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})(window, document);
