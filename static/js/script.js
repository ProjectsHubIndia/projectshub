/* ═══════════════════════════════════════════
   ProjectsHub — script.js
   Single source of truth for ALL JavaScript
   Covers: index.html, projects.html, workshop.html, workshop-day.html
   ═══════════════════════════════════════════ */

(function () {
  "use strict";

  /* ────────────────────────────────────────
       CSRF COOKIE HELPER  ← moved inside IIFE
       (was incorrectly outside — polluted global scope)
    ──────────────────────────────────────── */
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      var cookies = document.cookie.split(";");
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    // Fallback: read from <meta name="csrf-token"> if cookie not set
    if (!cookieValue && name === "csrftoken") {
      var meta = document.querySelector('meta[name="csrf-token"]');
      if (meta) cookieValue = meta.getAttribute("content");
    }
    return cookieValue;
  }

  /* ════════════════════════════════════════
       1. NAVBAR — Hamburger, Theme, Scroll, Pill
       ════════════════════════════════════════ */

  var navbar = document.getElementById("navbar");
  var hamburger = document.getElementById("hamburger");
  var mobileMenu = document.getElementById("mobileMenu");

  if (hamburger && navbar && mobileMenu) {
    var iconMenu = hamburger.querySelector(".icon-menu");
    var iconClose = hamburger.querySelector(".icon-close");

    function setMobileMenuState(isOpen) {
      mobileMenu.classList.toggle("is-open", isOpen);
      mobileMenu.classList.toggle("active", isOpen);
      navbar.classList.toggle("is-open", isOpen);
      if (iconMenu) iconMenu.classList.toggle("hidden", isOpen);
      if (iconClose) iconClose.classList.toggle("hidden", !isOpen);
      hamburger.setAttribute("aria-expanded", isOpen ? "true" : "false");
      mobileMenu.setAttribute("aria-hidden", isOpen ? "false" : "true");
      document.body.classList.toggle("menu-open", isOpen);
    }

    // ── Hamburger toggle ──
    hamburger.addEventListener("click", function () {
      var willOpen = !mobileMenu.classList.contains("is-open") && !mobileMenu.classList.contains("active");
      setMobileMenuState(willOpen);
    });

    // ── Accordion toggle for expandable items ──
    mobileMenu.querySelectorAll(".mob-btn--expand").forEach(function (btn) {
      if (btn.dataset.accordionBound) return;
      btn.dataset.accordionBound = "true";
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var item = btn.closest(".mob-item");
        if (!item) return;
        var isOpen = item.classList.toggle("is-open");
        item.classList.toggle("open", isOpen);
        btn.setAttribute("aria-expanded", isOpen ? "true" : "false");
      });
    });

    // ── Close on mobile navigation link tap ──
    mobileMenu
      .querySelectorAll("a.mobile-link, a.mobile-sublink, .btn-cta--mobile, .mob-sub-link, a.mob-btn, .mobile-contact-btn")
      .forEach(function (link) {
        link.addEventListener("click", function () {
          setMobileMenuState(false);
        });
      });

    // ── Close on Escape key press ──
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && (mobileMenu.classList.contains("is-open") || mobileMenu.classList.contains("active"))) {
        setMobileMenuState(false);
        hamburger.focus();
      }
    });

    // ── Close when resized to desktop viewport (> 991px) ──
    window.addEventListener("resize", function () {
      if (window.innerWidth > 991 && (mobileMenu.classList.contains("is-open") || mobileMenu.classList.contains("active"))) {
        setMobileMenuState(false);
      }
    });
  }

  // ── Universal Toast Notifications ──
  window.showToast = function (message, type) {
    type = type || "success";
    var container = document.getElementById("phToastContainer");
    if (!container) {
      container = document.createElement("div");
      container.id = "phToastContainer";
      container.className = "ph-toast-container";
      document.body.appendChild(container);
    }
    var toast = document.createElement("div");
    toast.className = "ph-toast ph-toast--" + type;
    toast.innerHTML = (type === "success" ? "✓ " : type === "error" ? "✕ " : "ℹ ") + message;
    container.appendChild(toast);
    requestAnimationFrame(function () {
      toast.classList.add("show");
    });
    setTimeout(function () {
      toast.classList.remove("show");
      setTimeout(function () {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 350);
    }, 4000);
  };

  // ── Theme Management (Pure Light Theme Default) ──
  function initTheme() {
    localStorage.removeItem("ph-theme-v3");
    localStorage.removeItem("ph-theme");
    localStorage.setItem("ph-theme", "light");
    if (document.body) document.body.classList.add("light");
    if (document.documentElement) document.documentElement.classList.add("light");
  }
  initTheme();

  function toggleTheme() {
    // Theme toggle retained as safe no-op if triggered
    initTheme();
  }

  var desktopThemeToggle = document.getElementById("themeToggleBtn");
  if (desktopThemeToggle) {
    desktopThemeToggle.addEventListener("click", toggleTheme);
  }
  var mobileThemeToggle = document.getElementById("mobileThemeToggleBtn");
  if (mobileThemeToggle) {
    mobileThemeToggle.addEventListener("click", toggleTheme);
  }

  // ── Navbar border on scroll ──
  if (navbar) {
    window.addEventListener(
      "scroll",
      function () {
        navbar.style.borderColor =
          (window.scrollY || window.pageYOffset) > 60
            ? "rgba(255,255,255,0.15)"
            : "";
      },
      { passive: true },
    );
  }

  // ── Sliding pill for desktop nav ──
  (function initPillSlider() {
    var nav = document.querySelector(".navbar__links");
    var pill = document.getElementById("pillSlider");
    var links = document.querySelectorAll(".nav-link");
    if (!nav || !pill || !links.length) return;

    var isInsideNav = false;

    function getActiveLink() {
      return document.querySelector(".nav-link.active");
    }

    var lastHoveredLink = getActiveLink() || links[0];

    function movePillTo(link) {
      if (!link) return;
      var rect = link.getBoundingClientRect();
      var navRect = nav.getBoundingClientRect();
      pill.style.left = rect.left - navRect.left + "px";
      pill.style.width = rect.width + "px";
    }

    // Initialize pill position on the active link
    var currentActive = getActiveLink();
    if (currentActive) {
      // Need a slight delay to ensure fonts/layout are rendered
      setTimeout(function () {
        movePillTo(currentActive);
        pill.style.opacity = "1";
      }, 50);
    } else {
      movePillTo(links[0]);
    }

    links.forEach(function (link) {
      link.addEventListener("mouseenter", function () {
        lastHoveredLink = link;
        movePillTo(link);
        pill.style.opacity = "1";
      });
    });

    nav.addEventListener("mouseenter", function () {
      isInsideNav = true;
      if (lastHoveredLink) {
        movePillTo(lastHoveredLink);
        pill.style.opacity = "1";
      }
    });

    nav.addEventListener("mouseleave", function () {
      isInsideNav = false;
      var currentActive = getActiveLink();
      if (currentActive) {
        lastHoveredLink = currentActive;
        movePillTo(currentActive);
        pill.style.opacity = "1";
      } else {
        pill.style.opacity = "0";
      }
    });

    window.addEventListener("resize", function () {
      var currentActive = getActiveLink();
      if (lastHoveredLink && isInsideNav) {
        movePillTo(lastHoveredLink);
      } else if (currentActive) {
        movePillTo(currentActive);
      }
    });

    // Listen for custom event to update pill
    window.addEventListener("updateNavPill", function () {
      var currentActive = getActiveLink();
      if (currentActive) {
        lastHoveredLink = currentActive;
        movePillTo(currentActive);
        pill.style.opacity = "1";
      } else {
        pill.style.opacity = "0";
      }
    });
  })();

  /* ════════════════════════════════════════
       2. ABOUT SECTION — Pills, Stats, Tilt
       ════════════════════════════════════════ */

  // ── Staggered tech pills ──
  function initPills() {
    var pills = document.querySelectorAll(".tech-pill");
    if (!pills.length) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var index = Array.from(pills).indexOf(entry.target);
          setTimeout(function () {
            entry.target.classList.add("visible");
          }, index * 60);
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.2 },
    );

    pills.forEach(function (pill) {
      observer.observe(pill);
    });
  }

  // ── Stat values fade-in ──
  function initStats() {
    var stats = document.querySelectorAll(".stat-value");
    if (!stats.length) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var index = Array.from(stats).indexOf(entry.target);
          setTimeout(function () {
            entry.target.classList.add("visible");
          }, index * 120);
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.1 },
    );

    stats.forEach(function (stat) {
      observer.observe(stat);
    });
  }

  // ── Breakout card tilt ──
  // FIX: was querySelector (only first card) → now querySelectorAll (all cards)
  function initCardTilt() {
    // Disabled tilt effect per user request
  }

  /* ════════════════════════════════════════
       3. PROJECT CARDS — Scroll reveal
       ════════════════════════════════════════ */

  function initProjectCards() {
    var cards = document.querySelectorAll(".project-card");
    if (!cards.length) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var index = Array.from(cards).indexOf(entry.target);
          setTimeout(function () {
            entry.target.classList.add("visible");
          }, index * 100);
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.1 },
    );

    cards.forEach(function (card) {
      observer.observe(card);
    });
  }

  /* ════════════════════════════════════════
       4. PROJECT FILTER TABS (projects.html)
       ════════════════════════════════════════ */

  function initProjectFilter() {
    var tabs = document.querySelectorAll(".filter-tab");
    var cards = document.querySelectorAll("#projectsGrid .project-card");
    var empty = document.getElementById("projectsEmpty");
    if (!tabs.length || !cards.length) return;

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        tabs.forEach(function (t) {
          t.classList.remove("active");
          t.setAttribute("aria-selected", "false");
        });
        tab.classList.add("active");
        tab.setAttribute("aria-selected", "true");

        var filter = tab.getAttribute("data-filter");
        var visible = 0;

        cards.forEach(function (card) {
          var tags = card.getAttribute("data-tags") || "";
          if (filter === "all" || tags.includes(filter)) {
            card.classList.remove("hidden");
            visible++;
          } else {
            card.classList.add("hidden");
          }
        });

        if (empty) empty.style.display = visible === 0 ? "block" : "none";
      });
    });
  }

  /* ════════════════════════════════════════
       5. READ MORE TOGGLE (project cards)
       ════════════════════════════════════════ */

  function initReadMore() {
    var descs = document.querySelectorAll(".project-card__desc");
    var maxChars = 110;

    descs.forEach(function (desc) {
      // Remove any existing button first (prevents duplicates on re-init)
      var existingBtn = desc.querySelector(".project-card__readmore");
      if (existingBtn) existingBtn.remove();

      var fullText = desc.textContent.trim().replace(/\s+/g, " ");
      if (fullText.length <= maxChars) return;

      var truncated = fullText.slice(0, maxChars).trim() + "... ";
      desc.dataset.fullText = fullText;
      desc.dataset.truncatedText = truncated;
      desc.dataset.isExpanded = "false";

      desc.innerHTML = "";
      var textNode = document.createTextNode(truncated);
      var btn = document.createElement("span");
      btn.className = "project-card__readmore";
      btn.textContent = "Read more";
      desc.appendChild(textNode);
      desc.appendChild(btn);

      // FIX: stopPropagation prevents click reaching parent card link
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        e.preventDefault();
        var expanded = desc.dataset.isExpanded === "true";
        desc.childNodes[0].nodeValue = expanded
          ? desc.dataset.truncatedText
          : desc.dataset.fullText + " ";
        btn.textContent = expanded ? "Read more" : "Show less";
        desc.dataset.isExpanded = expanded ? "false" : "true";
      });
    });
  }

  /* ════════════════════════════════════════
       6. PRICING — Card reveal
       (billing toggle removed — data-monthly/
        data-yearly attributes not in HTML)
       ════════════════════════════════════════ */

  function initPricingCards() {
    var cards = document.querySelectorAll(".pricing-card");
    if (!cards.length) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var index = Array.from(cards).indexOf(entry.target);
          setTimeout(function () {
            entry.target.classList.add("visible");
          }, index * 120);
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.1 },
    );

    cards.forEach(function (card) {
      observer.observe(card);
    });
  }

  /* ════════════════════════════════════════
       7. PROJECTS GATE MODAL (index.html)
       ════════════════════════════════════════ */

  function initProjectsModal() {
    var overlay = document.getElementById("projectsModalOverlay");
    var openBtn = document.getElementById("openProjectsModal");
    var closeBtn = document.getElementById("modalClose");
    var form = document.getElementById("projectsGateForm");
    if (!overlay || !openBtn || !form) return;

    function openModal() {
      overlay.classList.add("is-active");
      document.body.style.overflow = "hidden";
      setTimeout(function () {
        var nameField = document.getElementById("gateName");
        if (nameField) nameField.focus();
      }, 300);
    }

    function closeModal() {
      overlay.classList.remove("is-active");
      document.body.style.overflow = "";
    }

    openBtn.addEventListener("click", openModal);

    document.querySelectorAll(".project-gate-trigger").forEach(function (link) {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        openModal();
      });
    });

    if (closeBtn) closeBtn.addEventListener("click", closeModal);

    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) closeModal();
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && overlay.classList.contains("is-active"))
        closeModal();
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = document.getElementById("gateName");
      var email = document.getElementById("gateEmail");
      var college = document.getElementById("gateCollege");
      var valid = true;

      [name, email, college].forEach(function (el) {
        el.classList.remove("has-error");
      });

      if (!name.value.trim()) {
        name.classList.add("has-error");
        valid = false;
      }
      if (
        !email.value.trim() ||
        !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)
      ) {
        email.classList.add("has-error");
        valid = false;
      }
      if (!college.value.trim()) {
        college.classList.add("has-error");
        valid = false;
      }
      if (!valid) return;

      var payload = {
        full_name: name.value.trim(),
        email: email.value.trim(),
        college_or_org: college.value.trim(),
      };

      fetch("/gate/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify(payload),
      })
        .catch(function () {})
        .finally(function () {
          localStorage.setItem(
            "ph-project-user",
            JSON.stringify({
              name: payload.full_name,
              email: payload.email,
              college: payload.college_or_org,
              timestamp: new Date().toISOString(),
            }),
          );
          window.location.href = "/projects/";
        });
    });
  }



  /* ════════════════════════════════════════
       9. SPLINE LAZY LOADER (index.html)
       ════════════════════════════════════════ */

  // Shared flag — prevents aurora resume conflict between
  // initAuroraPause (scroll-based) and initSplineSmart (load-based)
  var splineLoading = false;

  function initSplineSmart() {
    var wrapper = document.getElementById("spline-wrapper");
    var iframe = document.getElementById("spline-frame");
    var loader = document.getElementById("spline-loader");
    if (!wrapper || !iframe || !loader) return;

    var isLoaded = false;
    var minDisplayTime = 1500;
    var loadStartTime = Date.now();
    var auroraBg = document.querySelector(".aurora-bg");

    function hideLoader() {
      if (isLoaded) return;
      isLoaded = true;
      var remaining = Math.max(
        0,
        minDisplayTime - (Date.now() - loadStartTime),
      );
      setTimeout(function () {
        loader.classList.add("is-hidden");
        setTimeout(function () {
          if (loader && loader.parentNode)
            loader.parentNode.removeChild(loader);
          splineLoading = false; // FIX: signal aurora it's safe to resume
          if (auroraBg) auroraBg.style.animationPlayState = "running";
        }, 700);
      }, remaining);
    }

    function loadSpline() {
      if (iframe.src || iframe.dataset.loaded) return;
      iframe.dataset.loaded = "true";

      splineLoading = true; // FIX: signal aurora to not resume during load
      if (auroraBg) auroraBg.style.animationPlayState = "paused";

      iframe.src = iframe.dataset.src;
      iframe.addEventListener("load", hideLoader);
      setTimeout(function () {
        if (!isLoaded) hideLoader();
      }, 10000);

      // Cover Spline watermark — FIX: was invalid fractional rgba, now clean hex
      var splineCover = document.createElement("div");
      splineCover.id = "spline-cover";
      splineCover.style.cssText = [
        "position:absolute",
        "bottom:0",
        "right:0",
        "width:100%",
        "height:57px",
        "background:#e3e3e3",
        "z-index:5",
        "pointer-events:none",
      ].join(";");
      wrapper.appendChild(splineCover);
    }

    // Trigger on first scroll / click / touch — not on page load
    var triggered = false;
    var fallbackTimer;

    function triggerLoad() {
      if (triggered) return;
      triggered = true;
      clearTimeout(fallbackTimer); // FIX: cancel fallback if user triggers early
      setTimeout(loadSpline, 300);
      window.removeEventListener("scroll", triggerLoad);
      window.removeEventListener("click", triggerLoad);
      window.removeEventListener("touchstart", triggerLoad);
    }

    // Fallback: load after 4s even if user never interacts
    fallbackTimer = setTimeout(triggerLoad, 4000);

    window.addEventListener("scroll", triggerLoad, { passive: true });
    window.addEventListener("click", triggerLoad);
    window.addEventListener("touchstart", triggerLoad, { passive: true });
  }

  // ── Pause aurora while scrolling (GPU relief) ──
  function initAuroraPause() {
    var auroraBg = document.querySelector(".aurora-bg");
    if (!auroraBg) return;

    var scrollTimer;
    window.addEventListener(
      "scroll",
      function () {
        auroraBg.style.animationPlayState = "paused";
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(function () {
          // FIX: don't resume if Spline is still initialising its WebGL context
          if (!splineLoading) {
            auroraBg.style.animationPlayState = "running";
          }
        }, 150);
      },
      { passive: true },
    );
  }

  /* ════════════════════════════════════════
       10. WORKSHOP — Day cards + Feature items
       ════════════════════════════════════════ */

  function initDayCards() {
    var cards = document.querySelectorAll(".day-card");
    if (!cards.length) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var index = Array.from(cards).indexOf(entry.target);
          setTimeout(function () {
            entry.target.classList.add("visible");
          }, index * 120);
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.1 },
    );

    cards.forEach(function (card) {
      observer.observe(card);
    });
  }

  function initFeatureItems() {
    var items = document.querySelectorAll(".feature-item");
    if (!items.length) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.1 },
    );

    items.forEach(function (item) {
      item.style.opacity = "0";
      item.style.transform = "translateY(20px)";
      item.style.transition = "opacity 0.5s ease, transform 0.5s ease";
      observer.observe(item);
    });
  }

  /* ════════════════════════════════════════
       11. WORKSHOP SHARE CARD (workshop.html)
       ════════════════════════════════════════ */

  function initShareCard() {
    var overlay = document.getElementById("shareOverlay");
    var closeBtn = document.getElementById("shareClose");
    if (!overlay) return;

    function openShare(dayCard) {
      document.getElementById("shareDay").textContent =
        "Day " + dayCard.dataset.day;
      document.getElementById("shareTitle").textContent = dayCard.dataset.title;
      document.getElementById("shareDate").textContent = dayCard.dataset.date;
      document.getElementById("shareDesc").textContent = dayCard.dataset.desc;
      document.getElementById("shareOutcomeText").textContent =
        "Outcome: " + dayCard.dataset.outcome;
      overlay.classList.add("is-active");
      document.body.style.overflow = "hidden";
    }

    function closeShare() {
      overlay.classList.remove("is-active");
      document.body.style.overflow = "";
    }

    document.querySelectorAll(".day-card__share-btn").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        openShare(btn.closest(".day-card"));
      });
    });

    if (closeBtn) closeBtn.addEventListener("click", closeShare);

    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) closeShare();
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && overlay.classList.contains("is-active"))
        closeShare();
    });

    // Copy link
    var copyBtn = document.getElementById("shareCopyLink");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        var day = document
          .getElementById("shareDay")
          .textContent.replace("Day ", "");
        var url = window.location.origin + "/workshop-day.html?day=" + day;
        navigator.clipboard.writeText(url).then(function () {
          copyBtn.textContent = "✓ Copied!";
          setTimeout(function () {
            copyBtn.innerHTML =
              '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy Link';
          }, 2000);
        });
      });
    }

    // WhatsApp
    var waBtn = document.getElementById("shareWhatsApp");
    if (waBtn) {
      waBtn.addEventListener("click", function () {
        var title = document.getElementById("shareTitle").textContent;
        var day = document.getElementById("shareDay").textContent;
        var url =
          window.location.origin +
          "/workshop-day.html?day=" +
          day.replace("Day ", "");
        window.open(
          "https://wa.me/?text=" +
            encodeURIComponent(
              "🚀 Check out *" +
                day +
                ": " +
                title +
                "* from the ProjectsHub AI Workshop!\n" +
                url,
            ),
          "_blank",
        );
      });
    }

    // Twitter / X
    var twBtn = document.getElementById("shareTwitter");
    if (twBtn) {
      twBtn.addEventListener("click", function () {
        var title = document.getElementById("shareTitle").textContent;
        var day = document.getElementById("shareDay").textContent;
        var url =
          window.location.origin +
          "/workshop-day.html?day=" +
          day.replace("Day ", "");
        window.open(
          "https://twitter.com/intent/tweet?text=" +
            encodeURIComponent(
              "🚀 " + day + ": " + title + " — ProjectsHub AI Workshop",
            ) +
            "&url=" +
            encodeURIComponent(url),
          "_blank",
        );
      });
    }
  }

  /* ════════════════════════════════════════
       12. WORKSHOP DAY DETAIL (workshop-day.html)
       ════════════════════════════════════════ */

  function initWorkshopDay() {
    var container = document.getElementById("dayDetail");
    if (!container) return;

    var DAYS = {
      1: {
        day: "Day 1",
        title: "Foundations of AI & Python for ML",
        date: "Sunday, May 10 · 10 AM – 5 PM IST",
        desc: "This opening day is all about building a rock-solid foundation. We start with a focused Python crash course tailored specifically for machine learning — covering essential syntax, data structures, and functional programming patterns you'll use daily. Then we dive deep into NumPy and Pandas, the backbone of every data pipeline, learning to manipulate, clean, and transform real-world datasets with confidence. By the afternoon, you'll be creating stunning visualizations with Matplotlib and Seaborn, and performing a complete Exploratory Data Analysis on a real dataset.",
        outcome:
          "Complete EDA on a real dataset — cleaned, analyzed, and visualized.",
        outcomeDetail:
          "You'll have a fully functional Jupyter notebook with a comprehensive analysis of a real-world dataset, including statistical summaries, correlation matrices, distribution plots, and actionable insights.",
        topics: [
          {
            name: "Python Crash Course for ML",
            sub: "Lists, dicts, comprehensions, lambda functions, OOP basics",
          },
          {
            name: "NumPy & Pandas Deep Dive",
            sub: "Array operations, DataFrames, groupby, merge, pivot tables",
          },
          {
            name: "Data Cleaning & Preprocessing",
            sub: "Missing values, outliers, encoding, normalization",
          },
          {
            name: "Exploratory Data Analysis",
            sub: "Statistical analysis, correlation, distribution analysis",
          },
          {
            name: "Matplotlib & Seaborn",
            sub: "Line, bar, scatter, heatmaps, pair plots, styling",
          },
          {
            name: "ML Environment Setup",
            sub: "Jupyter, Conda, Git, VS Code, project structure",
          },
        ],
      },
      2: {
        day: "Day 2",
        title: "Machine Learning Models & Training",
        date: "Monday, May 11 · 10 AM – 5 PM IST",
        desc: "The most intensive day of the workshop. We jump straight into supervised learning — starting with linear and logistic regression, then moving to powerful ensemble methods like Random Forests and Gradient Boosting. You'll learn to properly evaluate models using precision, recall, F1, ROC-AUC, and cross-validation. The afternoon is dedicated to feature engineering and hyperparameter tuning with GridSearch and Optuna. By end of day, you'll have built and deployed a complete price prediction model.",
        outcome:
          "Build a price prediction model with optimized hyperparameters.",
        outcomeDetail:
          "A production-ready regression model trained on real estate data, complete with feature engineering pipeline, cross-validated metrics, and hyperparameter optimization — all in a reproducible notebook.",
        topics: [
          {
            name: "Linear & Logistic Regression",
            sub: "Theory, implementation, regularization (L1/L2)",
          },
          {
            name: "Decision Trees & Random Forests",
            sub: "Splitting criteria, pruning, ensemble methods",
          },
          {
            name: "Model Evaluation & Metrics",
            sub: "Accuracy, precision, recall, F1, confusion matrix, ROC",
          },
          {
            name: "Hyperparameter Tuning",
            sub: "GridSearchCV, RandomizedSearch, Optuna",
          },
          {
            name: "Cross-Validation Strategies",
            sub: "K-Fold, Stratified, Leave-One-Out, time-series splits",
          },
          {
            name: "Feature Engineering",
            sub: "Polynomial features, binning, target encoding, selection",
          },
        ],
      },
      3: {
        day: "Day 3",
        title: "Deep Learning & Neural Networks",
        date: "Tuesday, May 12 · 10 AM – 5 PM IST",
        desc: "Today we unlock the power of deep learning. Starting from the mathematical foundations of neural networks — perceptrons, activation functions, backpropagation — we quickly move to building real models with TensorFlow and Keras. You'll implement convolutional neural networks (CNNs) for image classification and learn transfer learning with pre-trained models like ResNet and MobileNet. By end of day, you'll have an image classifier achieving 95%+ accuracy on a custom dataset.",
        outcome:
          "Image classifier achieving 95%+ accuracy on a custom dataset.",
        outcomeDetail:
          "A trained CNN model using transfer learning, with data augmentation, learning rate scheduling, and model checkpointing — exported and ready for inference.",
        topics: [
          {
            name: "Neural Network Architecture",
            sub: "Perceptrons, layers, activation functions, backprop",
          },
          {
            name: "TensorFlow / Keras Basics",
            sub: "Sequential API, functional API, callbacks, training loops",
          },
          {
            name: "Convolutional Neural Networks",
            sub: "Conv layers, pooling, architecture patterns",
          },
          {
            name: "Transfer Learning",
            sub: "ResNet, MobileNet, fine-tuning, feature extraction",
          },
          {
            name: "Image Classification Project",
            sub: "Data augmentation, training, evaluation, visualization",
          },
          {
            name: "Model Saving & Optimization",
            sub: "SavedModel, ONNX, quantization, TFLite",
          },
        ],
      },
      4: {
        day: "Day 4",
        title: "Deployment & Real-World APIs",
        date: "Wednesday, May 13 · 10 AM – 5 PM IST",
        desc: "The final day brings everything together. You'll learn to wrap your ML models in production-grade FastAPI endpoints, containerize them with Docker, and deploy to the cloud. We cover CI/CD pipelines for automated model retraining, monitoring with logging and alerting, and best practices for ML in production. The capstone project ties all 4 days together — a complete end-to-end ML application from data to deployment.",
        outcome: "Live deployed ML API accessible from anywhere.",
        outcomeDetail:
          "A Dockerized FastAPI application serving your trained model, deployed on AWS/GCP with health checks, structured logging, and a CI/CD pipeline for automated deployments.",
        topics: [
          {
            name: "FastAPI for ML Serving",
            sub: "Endpoints, Pydantic schemas, async handlers, file uploads",
          },
          {
            name: "Docker Containerization",
            sub: "Dockerfile, multi-stage builds, docker-compose",
          },
          {
            name: "Cloud Deployment",
            sub: "AWS EC2/Lambda, GCP Cloud Run, environment variables",
          },
          {
            name: "CI/CD for ML Pipelines",
            sub: "GitHub Actions, automated testing, model versioning",
          },
          {
            name: "Monitoring & Logging",
            sub: "Structured logs, health checks, alerting, metrics",
          },
          {
            name: "Capstone: End-to-End ML App",
            sub: "Full pipeline from data ingestion to live API",
          },
        ],
      },
    };

    var params = new URLSearchParams(window.location.search);
    var dayNum = params.get("day") || "1";
    var data = DAYS[dayNum] || DAYS["1"];
    var prev = parseInt(dayNum) > 1 ? parseInt(dayNum) - 1 : null;
    var next = parseInt(dayNum) < 4 ? parseInt(dayNum) + 1 : null;

    document.title = data.day + ": " + data.title + " — ProjectsHub Workshop";

    var topicsHTML = data.topics
      .map(function (t, i) {
        return (
          '<div class="topic-item">' +
          '<div class="topic-item__icon">' +
          (i + 1) +
          "</div>" +
          '<div class="topic-item__text">' +
          '<p class="topic-item__name">' +
          t.name +
          "</p>" +
          '<p class="topic-item__sub">' +
          t.sub +
          "</p>" +
          "</div></div>"
        );
      })
      .join("");

    var navHTML = '<div class="day-detail__nav">';
    if (prev) {
      navHTML +=
        '<a href="/workshop-day.html?day=' +
        prev +
        '" class="day-nav-btn">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="m12 19-7-7 7-7"/></svg>' +
        " Day " +
        prev +
        "</a>";
    } else {
      navHTML += "<span></span>";
    }

    navHTML +=
      '<a href="/workshop.html" class="day-nav-btn day-nav-btn--primary">Back to Workshop</a>';

    if (next) {
      navHTML +=
        '<a href="/workshop-day.html?day=' +
        next +
        '" class="day-nav-btn">Day ' +
        next +
        ' <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></a>';
    } else {
      navHTML += "<span></span>";
    }
    navHTML += "</div>";

    container.innerHTML =
      '<div class="day-detail__badge"><span class="day-detail__badge-dot"></span> 4-Day AI Workshop</div>' +
      '<p class="day-detail__day">' +
      data.day +
      "</p>" +
      '<h1 class="day-detail__title">' +
      data.title +
      "</h1>" +
      '<p class="day-detail__date"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg> ' +
      data.date +
      "</p>" +
      '<p class="day-detail__desc">' +
      data.desc +
      "</p>" +
      '<h2 class="day-detail__section-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg> Topics Covered</h2>' +
      '<div class="day-detail__topics-grid">' +
      topicsHTML +
      "</div>" +
      '<div class="day-detail__outcome">' +
      '<h3 class="day-detail__outcome-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> ' +
      data.outcome +
      "</h3>" +
      '<p class="day-detail__outcome-text">' +
      data.outcomeDetail +
      "</p>" +
      "</div>" +
      navHTML;
  }

  /* ════════════════════════════════════════
       13. LOGO CLICK → Home
       ════════════════════════════════════════ */

  function initLogoRedirect() {
    var logo = document.querySelector(".logo");
    if (!logo) return;
    logo.style.cursor = "pointer";
    logo.addEventListener("click", function () {
      window.location.href = "/";
    });
  }

  function initMarquee() {
    var winW = window.innerWidth;
    document.querySelectorAll(".marquee-track").forEach(function (track) {
      var original = track.innerHTML;
      var initialW = track.scrollWidth;
      if (!initialW) return;
      var targetW = winW * 2.5;
      var sets = Math.max(2, Math.ceil(targetW / initialW));
      var newHtml = "";
      for (var s = 0; s < sets; s++) {
        newHtml += original;
      }
      track.innerHTML = newHtml;

      var pct = ((1 / sets) * 100).toFixed(4);
      var isReverse = track.classList.contains("marquee-track--reverse");
      var id = track.id || "mq-" + Math.random().toString(36).slice(2);
      track.id = id;

      var style = document.createElement("style");
      style.textContent = isReverse
        ? "#" +
          id +
          " { animation-name: marquee-right-" +
          id +
          "; } " +
          "@keyframes marquee-right-" +
          id +
          " { from { transform: translateX(-" +
          pct +
          "%); } to { transform: translateX(0); } }"
        : "#" +
          id +
          " { animation-name: marquee-left-" +
          id +
          "; } " +
          "@keyframes marquee-left-" +
          id +
          " { from { transform: translateX(0); } to { transform: translateX(-" +
          pct +
          "%); } }";
      document.head.appendChild(style);
    });
  }
  /* ════════════════════════════════════════
       CONTACT FORM SUBMISSION
       ════════════════════════════════════════ */
  function initContactForm() {
    var form = document.getElementById("contactForm");
    if (!form) return;

    var captchaDisplay = document.getElementById("captchaDisplay");
    var captchaRefreshBtn = document.getElementById("captchaRefreshBtn");
    var captchaInput = document.getElementById("contactCaptcha");
    var currentCaptchaToken = "";

    function loadCaptcha() {
      if (!captchaDisplay) return;
      captchaDisplay.style.opacity = "0.5";
      fetch("/api/captcha/")
        .then(function (res) {
          return res.json();
        })
        .then(function (data) {
          if (data && data.success) {
            currentCaptchaToken = data.token || "";
            captchaDisplay.innerHTML = data.svg;
            if (captchaInput) captchaInput.value = "";
          }
        })
        .catch(function (err) {
          console.error("Catch code load error:", err);
          if (captchaDisplay) {
            captchaDisplay.innerHTML = '<span style="font-size:0.7rem;color:#ef4444;">Click refresh</span>';
          }
        })
        .finally(function () {
          if (captchaDisplay) captchaDisplay.style.opacity = "1";
        });
    }

    if (captchaRefreshBtn) {
      captchaRefreshBtn.addEventListener("click", function (e) {
        e.preventDefault();
        loadCaptcha();
      });
    }

    // Load initial catch code on setup
    loadCaptcha();

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var submitBtn = form.querySelector('button[type="submit"]');
      var originalContent = submitBtn ? submitBtn.innerHTML : "Send Message";

      var fullNameInput = form.querySelector('#contactName, [name="full_name"]');
      var emailInput = form.querySelector('#contactEmail, [name="email"]');
      var phoneInput = form.querySelector('#contactPhone, [name="phone"]');
      var subjectInput = form.querySelector('#contactSubject, [name="subject"]');
      var messageInput = form.querySelector('#contactMessage, [name="message"]');
      var catchCodeInput = form.querySelector('#contactCaptcha, [name="catch_code"]');
      var hpInput = form.querySelector('#contactHpFax, [name="hp_company_url"]');
      var sourcePageInput = form.querySelector('#contactSourcePage, [name="source_page"]');
      var statusEl = form.querySelector('#contactFormStatus') || document.getElementById('contactFormStatus');

      var fullName = fullNameInput ? fullNameInput.value.trim() : "";
      var email = emailInput ? emailInput.value.trim() : "";
      var phone = phoneInput ? phoneInput.value.trim() : "";
      var subject = subjectInput ? subjectInput.value.trim() : "";
      var message = messageInput ? messageInput.value.trim() : "";
      var catchCode = catchCodeInput ? catchCodeInput.value.trim() : "";
      var hpVal = hpInput ? hpInput.value.trim() : "";
      var sourcePage = sourcePageInput ? sourcePageInput.value.trim() : (window.location.pathname || "/#contact");

      if (statusEl) {
        statusEl.style.display = "none";
        statusEl.className = "contact-status-alert";
        statusEl.innerHTML = "";
      }

      if (!fullName || !email || !message) {
        if (statusEl) {
          statusEl.className = "contact-status-alert error";
          statusEl.textContent = "Please fill in your name, email, and message.";
          statusEl.style.display = "flex";
        }
        if (window.showToast) window.showToast("Please fill in your name, email, and message.", "error");
        return;
      }

      if (!catchCode) {
        if (statusEl) {
          statusEl.className = "contact-status-alert error";
          statusEl.textContent = "Please enter the security catch code.";
          statusEl.style.display = "flex";
        }
        if (window.showToast) window.showToast("Please enter the catch code (security verification).", "error");
        if (catchCodeInput) catchCodeInput.focus();
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Sending...';
      }

      var csrfToken = getCookie("csrftoken");

      fetch("/contact/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          full_name: fullName,
          email: email,
          phone: phone,
          subject: subject,
          message: message,
          source_page: sourcePage,
          catch_code: catchCode,
          captcha_token: currentCaptchaToken,
          hp_company_url: hpVal,
        }),
      })
        .then(function (res) {
          return res.json().then(function (data) {
            return { ok: res.ok, status: res.status, data: data };
          });
        })
        .then(function (resObj) {
          var data = resObj.data;
          if (resObj.ok && data && data.success) {
            form.reset();
            loadCaptcha();
            var successMsg = data.message || "Thank you! We've received your message and will reach out shortly.";
            if (statusEl) {
              statusEl.className = "contact-status-alert success";
              statusEl.textContent = successMsg;
              statusEl.style.display = "flex";
            }
            if (window.showToast) {
              window.showToast(successMsg, "success");
            }
          } else {
            var errMsg = "Failed to submit message. Please try again.";
            if (data && data.errors && data.errors.catch_code) {
              errMsg = data.errors.catch_code;
            } else if (data && data.errors) {
              var firstErrKey = Object.keys(data.errors)[0];
              errMsg = data.errors[firstErrKey];
            } else if (data && data.message) {
              errMsg = data.message;
            }
            if (statusEl) {
              statusEl.className = "contact-status-alert error";
              statusEl.textContent = errMsg;
              statusEl.style.display = "flex";
            }
            if (window.showToast) window.showToast(errMsg, "error");
            loadCaptcha();
            if (catchCodeInput) {
              catchCodeInput.value = "";
              catchCodeInput.focus();
            }
          }
        })
        .catch(function (err) {
          console.error("Contact form error:", err);
          var netErrMsg = "Network error. Please try again or email us directly.";
          if (statusEl) {
            statusEl.className = "contact-status-alert error";
            statusEl.textContent = netErrMsg;
            statusEl.style.display = "flex";
          }
          if (window.showToast) {
            window.showToast(netErrMsg, "error");
          }
          loadCaptcha();
        })
        .finally(function () {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalContent;
          }
        });
    });
  }

  /* ════════════════════════════════════════
       INIT — Run everything on DOMContentLoaded
       ════════════════════════════════════════ */

  function init() {
    // Shared across all pages
    initAuroraPause();

    // index.html
    initPills();
    initStats();
    initCardTilt();
    initProjectCards();
    initReadMore();
    initPricingCards();
    initProjectsModal();
    initContactForm();
    initSplineSmart();
    initLogoRedirect();
    initMarquee();
    // projects.html
    initProjectFilter();

    // workshop.html
    initDayCards();
    initFeatureItems();
    initShareCard();

    // workshop-day.html
    initWorkshopDay();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
