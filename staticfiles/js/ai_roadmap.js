/* ═══════════════════════════════════════════════════════════════════════════
   ProjectsHub — AI Engineer Roadmap
   ---------------------------------------------------------------------------
   Chapters, topics and drawer content are rendered by Django and handed over
   as JSON (#roadmapTopicsData / #roadmapConfigData) — nothing is hardcoded
   here any more. Manage it all under "Roadmap" in the admin.
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  // ── Data from the backend ────────────────────────────────────────────────
  function readJSON(id, fallback) {
    var el = document.getElementById(id);
    if (!el) return fallback;
    try {
      return JSON.parse(el.textContent) || fallback;
    } catch (e) {
      return fallback;
    }
  }

  var TOPICS = readJSON("roadmapTopicsData", {});
  var CONFIG = readJSON("roadmapConfigData", {});
  var PROJECTS_URL = CONFIG.projectsUrl || "/projects/";
  var WORKSHOP_URL = CONFIG.workshopUrl || "/workshop/";
  var BADGE_LABEL = CONFIG.badgeLabel || "AI Engineering Deep Dive";

  var DONE_KEY = "ph_roadmap_done_v1";

  // ── Small helpers ───────────────────────────────────────────────────────
  function esc(value) {
    var d = document.createElement("div");
    d.textContent = value == null ? "" : String(value);
    return d.innerHTML;
  }

  function isSafeUrl(url) {
    // Only allow links we rendered ourselves: absolute http(s), or site-relative.
    return typeof url === "string" && /^(https?:\/\/|\/|#)/i.test(url.trim());
  }

  function readDone() {
    try {
      var raw = window.localStorage.getItem(DONE_KEY);
      var parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
      return [];
    }
  }

  function writeDone(list) {
    try {
      window.localStorage.setItem(DONE_KEY, JSON.stringify(list));
    } catch (e) {
      /* private mode / blocked storage — progress just will not persist */
    }
  }

  var doneSet = (function () {
    var set = Object.create(null);
    readDone().forEach(function (key) {
      if (TOPICS[key]) set[key] = true;
    });
    return set;
  })();

  function doneKeys() {
    return Object.keys(doneSet);
  }

  // ── Resource fallbacks for topics with no curated links ─────────────────
  function withFallbacks(key, data) {
    var title = data.title || key.replace(/_/g, " ");
    var slug = key.replace(/_/g, "-");
    var ask = function (prompt) {
      return "https://chatgpt.com/?q=" + encodeURIComponent(prompt);
    };

    var free = data.free && data.free.length ? data.free : [
      {
        type: "docs",
        label: "Documentation",
        title: title + " — Specifications & Reference Guide",
        url: "https://www.google.com/search?q=" +
          encodeURIComponent(title + " developer documentation API guide")
      },
      {
        type: "video",
        label: "YouTube",
        title: title + " Architecture & Hands-on Masterclass",
        url: "https://www.youtube.com/results?search_query=" +
          encodeURIComponent(title + " tutorial AI engineering full guide")
      },
      {
        type: "article",
        label: "Guide",
        title: "Production System Patterns for " + title,
        url: "https://github.com/topics/" + encodeURIComponent(slug)
      }
    ];

    var tutor = data.tutor && data.tutor.length ? data.tutor : [
      {
        type: "tutor",
        label: "AI Tutor",
        title: 'Interactive Prompt: Explain "' + title + '" with code examples & mental models',
        url: ask(
          "Act as an expert AI Engineer and teacher. Teach me " + title +
          " step-by-step. Provide: 1) Intuitive explanation, 2) Production code snippet, " +
          "3) Common pitfalls and how to debug them."
        )
      },
      {
        type: "course",
        label: "Architecture",
        title: "System Design Drill: Evaluating " + title + " in Production Pipelines",
        url: ask(
          "Give me a challenging real-world engineering problem involving " + title +
          " and guide me through solving it interactively."
        )
      }
    ];

    var premium = data.premium && data.premium.length ? data.premium : [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Production Project with Source Code: " + title + " System",
        url: PROJECTS_URL
      },
      {
        type: "course",
        label: "Bootcamp",
        title: "ProjectsHub 1-on-1 AI Mentorship & Engineering Workshop",
        url: WORKSHOP_URL
      }
    ];

    return { free: free, tutor: tutor, premium: premium };
  }

  // ── Topic drawer ────────────────────────────────────────────────────────
  var overlay, dialog, lastTrigger = null;

  function renderLinks(items) {
    if (!items || !items.length) {
      return '<p class="resource-empty">No resources available yet.</p>';
    }
    return items.map(function (item) {
      var safe = isSafeUrl(item.url);
      var href = safe ? item.url : "#";
      var external = safe && /^https?:\/\//i.test(item.url);
      return (
        '<a href="' + esc(href) + '" class="resource-link"' +
        (external ? ' target="_blank" rel="noopener noreferrer"' : "") +
        (safe ? "" : ' aria-disabled="true"') + ">" +
        '<span class="resource-type ' + esc(item.type || "article") + '">' +
        esc(item.label || "Resource") + "</span>" +
        '<span class="resource-title">' + esc(item.title) + "</span>" +
        '<i class="fa-solid ' + (external ? "fa-arrow-up-right-from-square" : "fa-arrow-right") +
        ' resource-arrow" aria-hidden="true"></i>' +
        "</a>"
      );
    }).join("");
  }

  function setText(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function setHTML(id, value) {
    var el = document.getElementById(id);
    if (el) el.innerHTML = value;
  }

  function openRoadmapModal(key, trigger) {
    if (!overlay) return;
    var raw = TOPICS[key];
    if (!raw) return;

    var data = withFallbacks(key, raw);

    document.querySelectorAll(".tag.active").forEach(function (t) {
      t.classList.remove("active");
    });
    lastTrigger = trigger || document.querySelector('.tag[data-topic="' + key + '"]');
    if (lastTrigger) lastTrigger.classList.add("active");

    setText("modalBadgeText", raw.chapter || BADGE_LABEL);
    setText("modalTitle", raw.title || key.replace(/_/g, " "));
    setHTML(
      "modalDesc",
      raw.desc ||
        "<p>Practical architecture guidelines and production implementations for <strong>" +
          esc(raw.title || key) + "</strong>.</p>"
    );

    setHTML("freeList", renderLinks(data.free));
    setHTML("tutorList", renderLinks(data.tutor));
    setHTML("premiumList", renderLinks(data.premium));

    var wrap = document.getElementById("modalImageWrap");
    var img = document.getElementById("modalImage");
    if (wrap && img) {
      if (raw.image) {
        img.src = raw.image;
        img.alt = raw.title || "";
        setText("modalImageLabel", raw.title || "");
        wrap.hidden = false;
      } else {
        wrap.hidden = true;
        img.removeAttribute("src");
      }
    }

    syncDoneToggle(key);
    overlay.dataset.topic = key;

    var body = document.getElementById("roadmapModalBody");
    if (body) body.scrollTop = 0;

    lockScroll(true);
    overlay.classList.add("open");
    overlay.setAttribute("aria-hidden", "false");
    document.body.classList.add("roadmap-drawer-open");

    var closeBtn = document.getElementById("modalCloseBtn");
    if (closeBtn) closeBtn.focus({ preventScroll: true });

    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, "", "#" + key);
    }
  }

  function closeRoadmapModal() {
    if (!overlay || !overlay.classList.contains("open")) return;
    overlay.classList.remove("open");
    overlay.setAttribute("aria-hidden", "true");
    document.body.classList.remove("roadmap-drawer-open");
    lockScroll(false);
    delete overlay.dataset.topic;

    document.querySelectorAll(".tag.active").forEach(function (t) {
      t.classList.remove("active");
    });

    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, "", window.location.pathname + window.location.search);
    }

    if (lastTrigger && document.contains(lastTrigger)) {
      lastTrigger.focus({ preventScroll: true });
    }
    lastTrigger = null;
  }

  // Keep the page from jumping when the scrollbar disappears.
  function lockScroll(on) {
    if (on) {
      var gap = window.innerWidth - document.documentElement.clientWidth;
      if (gap > 0) document.body.style.paddingRight = gap + "px";
      document.body.style.overflow = "hidden";
      document.documentElement.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
      document.documentElement.style.overflow = "";
      document.body.style.paddingRight = "";
    }
  }

  function trapFocus(event) {
    if (event.key !== "Tab" || !overlay || !overlay.classList.contains("open")) return;
    var focusables = dialog.querySelectorAll(
      'a[href], button:not([disabled]), input, [tabindex]:not([tabindex="-1"])'
    );
    if (!focusables.length) return;
    var first = focusables[0];
    var last = focusables[focusables.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  // ── "Mark as done" progress ─────────────────────────────────────────────
  function syncDoneToggle(key) {
    var btn = document.getElementById("modalDoneToggle");
    if (!btn) return;
    var isDone = !!doneSet[key];
    btn.classList.toggle("is-done", isDone);
    btn.setAttribute("aria-pressed", isDone ? "true" : "false");
    var label = btn.querySelector(".done-label");
    if (label) label.textContent = isDone ? "Completed" : "Mark as done";
  }

  function toggleDone() {
    var key = overlay && overlay.dataset.topic;
    if (!key) return;
    if (doneSet[key]) delete doneSet[key];
    else doneSet[key] = true;
    writeDone(doneKeys());
    syncDoneToggle(key);
    paintDone();
    renderProgress();
  }

  function paintDone() {
    document.querySelectorAll(".tag[data-topic]").forEach(function (tag) {
      tag.classList.toggle("is-done", !!doneSet[tag.dataset.topic]);
    });
  }

  function renderProgress() {
    var total = Object.keys(TOPICS).length;
    var done = doneKeys().length;
    var pct = total ? Math.round((done / total) * 100) : 0;

    setText("roadmapDoneCount", String(done));
    setText("roadmapDoneTotal", String(total));
    var bar = document.getElementById("roadmapDoneBar");
    if (bar) {
      bar.style.width = pct + "%";
      var meter = bar.parentElement;
      if (meter) meter.setAttribute("aria-valuenow", String(pct));
    }
    setText("roadmapDonePct", pct + "%");

    document.querySelectorAll(".timeline-item").forEach(function (item) {
      var tags = item.querySelectorAll(".tag[data-topic]");
      var complete = tags.length > 0;
      tags.forEach(function (t) {
        if (!doneSet[t.dataset.topic]) complete = false;
      });
      item.classList.toggle("chapter-complete", complete);
      var step = document.querySelector('.stepper-step[data-node="' + item.id + '"]');
      if (step) step.classList.toggle("is-complete", complete);
    });
  }

  function resetProgress() {
    doneSet = Object.create(null);
    writeDone([]);
    paintDone();
    renderProgress();
    var key = overlay && overlay.dataset.topic;
    if (key) syncDoneToggle(key);
  }

  // ── Topic search ────────────────────────────────────────────────────────
  function initSearch() {
    var input = document.getElementById("roadmapSearch");
    if (!input) return;
    var clear = document.getElementById("roadmapSearchClear");
    var status = document.getElementById("roadmapSearchCount");

    function run() {
      var q = input.value.trim().toLowerCase();
      var matches = 0;

      document.querySelectorAll(".tag[data-topic]").forEach(function (tag) {
        var hit = !q || tag.textContent.toLowerCase().indexOf(q) !== -1;
        tag.classList.toggle("is-filtered-out", !hit);
        if (hit && q) matches++;
      });

      // Hide sub-sections and chapters that have nothing left to show.
      document.querySelectorAll(".sub-category").forEach(function (sub) {
        sub.classList.toggle("is-filtered-out", q ? !sub.querySelector(".tag:not(.is-filtered-out)") : false);
      });
      document.querySelectorAll(".timeline-item").forEach(function (item) {
        item.classList.toggle("is-filtered-out", q ? !item.querySelector(".tag:not(.is-filtered-out)") : false);
      });

      document.body.classList.toggle("roadmap-filtering", !!q);
      if (clear) clear.hidden = !q;
      if (status) {
        status.textContent = q
          ? matches + (matches === 1 ? " topic" : " topics") + " found"
          : "";
      }
    }

    var timer;
    input.addEventListener("input", function () {
      window.clearTimeout(timer);
      timer = window.setTimeout(run, 120);
    });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        input.value = "";
        run();
      }
    });
    if (clear) {
      clear.hidden = true;
      clear.addEventListener("click", function () {
        input.value = "";
        run();
        input.focus();
      });
    }
  }

  // ── Sidebar stepper ─────────────────────────────────────────────────────
  function initStepper() {
    var container = document.getElementById("stepperContainer");
    var items = document.querySelectorAll(".timeline-item");
    if (!container || !items.length) return;

    var steps = "";
    items.forEach(function (item, index) {
      if (!item.id) item.id = "timeline-node-" + index;
      var heading = item.querySelector("h2, h3");
      var title = heading ? heading.textContent.replace(/^[0-9]+\.\s*/, "") : "Chapter " + (index + 1);
      steps +=
        '<button type="button" class="stepper-step" data-node="' + esc(item.id) + '">' +
        '<span class="step-number">' + (index + 1) + "</span>" +
        '<span class="step-title">' + esc(title) + "</span>" +
        "</button>";
    });

    container.innerHTML =
      '<div class="stepper-nav-outer">' +
      '<button type="button" class="stepper-arrow stepper-arrow-left" id="stepperArrowLeft" aria-label="Scroll chapters back">&#8249;</button>' +
      '<div class="stepper-wrapper" id="stepperScrollArea">' + steps + "</div>" +
      '<button type="button" class="stepper-arrow stepper-arrow-right" id="stepperArrowRight" aria-label="Scroll chapters forward">&#8250;</button>' +
      "</div>";

    var area = document.getElementById("stepperScrollArea");
    var left = document.getElementById("stepperArrowLeft");
    var right = document.getElementById("stepperArrowRight");
    var STEP = 200;

    function updateArrows() {
      if (!area || !left || !right) return;
      var scrollable = area.scrollWidth - area.clientWidth;
      // Vertical on desktop, horizontal on mobile — hide arrows when there is no overflow.
      var hidden = scrollable <= 1;
      left.hidden = hidden;
      right.hidden = hidden;
      left.style.opacity = area.scrollLeft > 0 ? "1" : "0.3";
      right.style.opacity = area.scrollLeft < scrollable - 1 ? "1" : "0.3";
    }

    if (left) left.addEventListener("click", function () { area.scrollBy({ left: -STEP, behavior: "smooth" }); });
    if (right) right.addEventListener("click", function () { area.scrollBy({ left: STEP, behavior: "smooth" }); });
    if (area) area.addEventListener("scroll", updateArrows, { passive: true });
    window.addEventListener("resize", updateArrows);
    updateArrows();

    container.addEventListener("click", function (e) {
      if (!e.target || typeof e.target.closest !== "function") return;
      var step = e.target.closest(".stepper-step");
      if (step && step.dataset.node) scrollToNode(step.dataset.node);
    });
  }

  function scrollToNode(nodeId) {
    var node = document.getElementById(nodeId);
    if (!node) return;
    var y = node.getBoundingClientRect().top + window.scrollY - 80;
    window.scrollTo({ top: y, behavior: "smooth" });
  }

  // ── One rAF-driven loop for every scroll effect ─────────────────────────
  function initScrollEffects() {
    var timeline = document.querySelector(".timeline");
    var icons = document.querySelectorAll(".timeline-icon");
    var badge = document.getElementById("timelineProgressBadge");
    var badgeText = document.getElementById("timelineProgressText");
    var borders = {
      top: document.getElementById("borderTop"),
      right: document.getElementById("borderRight"),
      bottom: document.getElementById("borderBottom"),
      left: document.getElementById("borderLeft")
    };
    var steps = document.querySelectorAll(".stepper-step");
    var items = document.querySelectorAll(".timeline-item");
    var queued = false;

    function segment(progress, start, end) {
      if (progress <= start) return 0;
      if (progress >= end) return 100;
      return ((progress - start) / (end - start)) * 100;
    }

    function frame() {
      queued = false;
      var maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      var progress = Math.min(100, Math.max(0, (window.scrollY / maxScroll) * 100));

      if (timeline) {
        timeline.style.setProperty("--scroll-progress", progress + "%");

        var rect = timeline.getBoundingClientRect();
        var fillBottom = rect.top + window.scrollY + (progress / 100) * timeline.offsetHeight;

        icons.forEach(function (icon) {
          var iconRect = icon.getBoundingClientRect();
          var center = iconRect.top + window.scrollY + iconRect.height / 2;
          icon.classList.toggle("filled", fillBottom >= center);
        });

        if (badge && badgeText) {
          var rounded = Math.round(progress);
          badgeText.textContent = rounded + "%";
          badge.style.position = "absolute";
          badge.style.top = (rect.top + window.scrollY + (progress / 100) * timeline.offsetHeight) + "px";
          badge.style.left = (rect.left + timeline.offsetWidth / 2) + "px";
          badge.style.transform = "translate(-50%, -50%)";
          badge.style.opacity = rounded <= 0 || rounded >= 100 ? "0" : "1";
        }
      }

      // Highlight the chapter nearest the top of the viewport.
      if (steps.length && items.length) {
        var activeIndex = 0;
        items.forEach(function (item, i) {
          if (item.getBoundingClientRect().top <= 140) activeIndex = i;
        });
        steps.forEach(function (step, i) {
          step.classList.toggle("is-active", i === activeIndex);
        });
      }

      if (borders.top) {
        if (window.innerWidth > 768) {
          borders.top.style.width = "0";
          borders.right.style.height = "0";
          borders.bottom.style.width = "0";
          borders.left.style.height = "0";
        } else {
          borders.top.style.width = segment(progress, 0, 25) + "vw";
          borders.right.style.height = segment(progress, 25, 50) + "vh";
          borders.bottom.style.width = segment(progress, 50, 75) + "vw";
          borders.left.style.height = segment(progress, 75, 100) + "vh";
        }
      }
    }

    function request() {
      if (queued) return;
      queued = true;
      window.requestAnimationFrame(frame);
    }

    window.addEventListener("scroll", request, { passive: true });
    window.addEventListener("resize", request);
    frame();
  }

  // ── Boot ────────────────────────────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", function () {
    // This page is light-only.
    document.documentElement.classList.remove("dark");
    document.documentElement.classList.add("light");
    document.body.classList.remove("dark", "ai-roadmap-dark");
    document.body.classList.add("light", "light-mode");

    overlay = document.getElementById("roadmapModalOverlay");
    dialog = document.getElementById("roadmapModalDialog");

    // Reparent so no ancestor stacking context can clip the drawer.
    if (overlay && overlay.parentElement !== document.body) {
      document.body.appendChild(overlay);
    }

    // Open a topic from any tag, anywhere on the page.
    document.addEventListener("click", function (e) {
      if (!e.target || typeof e.target.closest !== "function") return;
      var tag = e.target.closest(".tag[data-topic]");
      if (!tag) return;
      e.preventDefault();
      openRoadmapModal(tag.dataset.topic, tag);
    });

    var backdrop = document.getElementById("roadmapModalBackdrop");
    var closeBtn = document.getElementById("modalCloseBtn");
    var footerClose = document.getElementById("modalFooterClose");
    var doneToggle = document.getElementById("modalDoneToggle");

    if (backdrop) backdrop.addEventListener("click", closeRoadmapModal);
    if (closeBtn) closeBtn.addEventListener("click", closeRoadmapModal);
    if (footerClose) footerClose.addEventListener("click", closeRoadmapModal);
    if (doneToggle) doneToggle.addEventListener("click", toggleDone);
    if (dialog) dialog.addEventListener("click", function (e) { e.stopPropagation(); });

    var reset = document.getElementById("roadmapResetProgress");
    if (reset) reset.addEventListener("click", resetProgress);

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeRoadmapModal();
      trapFocus(e);
    });

    initStepper();
    initSearch();
    initScrollEffects();
    paintDone();
    renderProgress();

    // Deep link: /ai-roadmap/#rag_term opens that topic.
    var hash = decodeURIComponent(window.location.hash.replace("#", ""));
    if (hash && TOPICS[hash]) {
      window.setTimeout(function () { openRoadmapModal(hash); }, 250);
    } else if (hash) {
      var chapter = document.getElementById(hash);
      if (chapter) window.setTimeout(function () { scrollToNode(hash); }, 150);
    }
  });

  // Public API — kept for inline callers and other scripts.
  window.openDrawer = openRoadmapModal;
  window.openRoadmapModal = openRoadmapModal;
  window.closeRoadmapModal = closeRoadmapModal;
  window.scrollToNode = scrollToNode;
})();
