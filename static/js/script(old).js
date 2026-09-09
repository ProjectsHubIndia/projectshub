/* ═══════════════════════════════════════════
   ProjectsHub — script.js
   Single source of truth for ALL JavaScript
   Covers: index.html, projects.html, workshop.html, workshop-day.html
   ═══════════════════════════════════════════ */

(function () {
    'use strict';

    /* ════════════════════════════════════════
       1. NAVBAR — Hamburger, Theme, Scroll, Pill
       ════════════════════════════════════════ */

    var navbar = document.getElementById('navbar');
    var hamburger = document.getElementById('hamburger');
    var mobileMenu = document.getElementById('mobileMenu');
    var themeToggle = document.getElementById('themeToggle');

    if (hamburger && navbar && mobileMenu) {

        var iconMenu = hamburger.querySelector('.icon-menu');
        var iconClose = hamburger.querySelector('.icon-close');

        // ── Hamburger toggle ──
        hamburger.addEventListener('click', function () {
            var isOpen = mobileMenu.classList.toggle('is-open');
            navbar.classList.toggle('is-open', isOpen);
            iconMenu.classList.toggle('hidden', isOpen);
            iconClose.classList.toggle('hidden', !isOpen);
            hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
            mobileMenu.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
        });

        // ── Close on mobile link tap ──
        document.querySelectorAll('.mobile-link, .btn-cta--mobile').forEach(function (link) {
            link.addEventListener('click', function () {
                mobileMenu.classList.remove('is-open');
                navbar.classList.remove('is-open');
                iconMenu.classList.remove('hidden');
                iconClose.classList.add('hidden');
                hamburger.setAttribute('aria-expanded', 'false');
                mobileMenu.setAttribute('aria-hidden', 'true');
            });
        });
    }

    // ── Theme Toggle ──
    if (themeToggle) {
        var iconSun = themeToggle.querySelector('.icon-sun');
        var iconMoon = themeToggle.querySelector('.icon-moon');
    
        function applyTheme(isLight) {
            document.body.classList.toggle('light', isLight);
            if (iconSun && iconMoon) {
                iconSun.classList.toggle('hidden', isLight);
                iconMoon.classList.toggle('hidden', !isLight);
            }
            localStorage.setItem('ph-theme', isLight ? 'light' : 'dark');
        }
    
        // ── CHANGE THIS LINE — always default to light ──
        var savedTheme = localStorage.getItem('ph-theme');
        applyTheme(savedTheme !== 'dark');   // light unless user explicitly chose dark
    
        themeToggle.addEventListener('click', function () {
            applyTheme(!document.body.classList.contains('light'));
        });
    }

    // ── Navbar border on scroll ──
    if (navbar) {
        window.addEventListener('scroll', function () {
            navbar.style.borderColor = (window.scrollY || window.pageYOffset) > 60
                ? 'rgba(255,255,255,0.15)'
                : '';
        }, { passive: true });
    }

    // ── Sliding pill for desktop nav ──
    (function initPillSlider() {
        var nav = document.querySelector('.navbar__links');
        var pill = document.getElementById('pillSlider');
        var links = document.querySelectorAll('.nav-link');
        if (!nav || !pill || !links.length) return;

        var lastHoveredLink = links[0];
        var isInsideNav = false;

        function movePillTo(link) {
            var rect = link.getBoundingClientRect();
            var navRect = nav.getBoundingClientRect();
            pill.style.left = (rect.left - navRect.left) + 'px';
            pill.style.width = rect.width + 'px';
        }

        movePillTo(links[0]);

        links.forEach(function (link) {
            link.addEventListener('mouseenter', function () {
                lastHoveredLink = link;
                movePillTo(link);
            });
        });

        nav.addEventListener('mouseenter', function () {
            isInsideNav = true;
            if (lastHoveredLink) {
                movePillTo(lastHoveredLink);
                pill.style.opacity = '1';
            }
        });

        nav.addEventListener('mouseleave', function () {
            isInsideNav = false;
            pill.style.opacity = '0';
        });

        window.addEventListener('resize', function () {
            if (lastHoveredLink && isInsideNav) movePillTo(lastHoveredLink);
        });
    })();


    /* ════════════════════════════════════════
       2. ABOUT SECTION — Pills, Stats, Tilt
       ════════════════════════════════════════ */

    // ── Staggered tech pills ──
    function initPills() {
        var pills = document.querySelectorAll('.tech-pill');
        if (!pills.length) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var index = Array.from(pills).indexOf(entry.target);
                setTimeout(function () {
                    entry.target.classList.add('visible');
                }, index * 60);
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.2 });

        pills.forEach(function (pill) { observer.observe(pill); });
    }

    // ── Stat values fade-in ──
    function initStats() {
        var stats = document.querySelectorAll('.stat-value');
        if (!stats.length) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var index = Array.from(stats).indexOf(entry.target);
                setTimeout(function () {
                    entry.target.classList.add('visible');
                }, index * 120);
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.1 });

        stats.forEach(function (stat) { observer.observe(stat); });
    }

    // ── Breakout card tilt ──
    function initCardTilt() {
        var card = document.querySelector('.breakout-card');
        if (!card) return;

        card.addEventListener('mousemove', function (e) {
            var rect = card.getBoundingClientRect();
            var dx = (e.clientX - (rect.left + rect.width / 2)) / (rect.width / 2);
            var dy = (e.clientY - (rect.top + rect.height / 2)) / (rect.height / 2);
            card.style.transform = 'perspective(800px) rotateX(' + (-dy * 4).toFixed(2) + 'deg) rotateY(' + (dx * 4).toFixed(2) + 'deg) translateY(-2px)';
        });

        card.addEventListener('mouseleave', function () {
            card.style.transform = '';
        });
    }


    /* ════════════════════════════════════════
       3. PROJECT CARDS — Scroll reveal
       ════════════════════════════════════════ */

    function initProjectCards() {
        var cards = document.querySelectorAll('.project-card');
        if (!cards.length) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var index = Array.from(cards).indexOf(entry.target);
                setTimeout(function () {
                    entry.target.classList.add('visible');
                }, index * 100);
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.1 });

        cards.forEach(function (card) { observer.observe(card); });
    }


    /* ════════════════════════════════════════
       4. PROJECT FILTER TABS (projects.html)
       ════════════════════════════════════════ */

    function initProjectFilter() {
        var tabs = document.querySelectorAll('.filter-tab');
        var cards = document.querySelectorAll('#projectsGrid .project-card');
        var empty = document.getElementById('projectsEmpty');
        if (!tabs.length || !cards.length) return;

        tabs.forEach(function (tab) {
            tab.addEventListener('click', function () {
                tabs.forEach(function (t) { t.classList.remove('active'); });
                tab.classList.add('active');

                var filter = tab.getAttribute('data-filter');
                var visible = 0;

                cards.forEach(function (card) {
                    var tags = card.getAttribute('data-tags') || '';
                    if (filter === 'all' || tags.includes(filter)) {
                        card.classList.remove('hidden');
                        visible++;
                    } else {
                        card.classList.add('hidden');
                    }
                });

                if (empty) empty.style.display = visible === 0 ? 'block' : 'none';
            });
        });
    }


    /* ════════════════════════════════════════
       5. READ MORE TOGGLE (project cards)
       ════════════════════════════════════════ */

    function initReadMore() {
        var descs = document.querySelectorAll('.project-card__desc');
        var maxChars = 110;

        descs.forEach(function (desc) {
            var existingBtn = desc.querySelector('.project-card__readmore');
            if (existingBtn) existingBtn.remove();

            var fullText = desc.textContent.trim().replace(/\s+/g, ' ');
            if (fullText.length <= maxChars) return;

            var truncated = fullText.slice(0, maxChars).trim() + '... ';
            desc.dataset.fullText = fullText;
            desc.dataset.truncatedText = truncated;
            desc.dataset.isExpanded = 'false';

            desc.innerHTML = '';
            var textNode = document.createTextNode(truncated);
            var btn = document.createElement('span');
            btn.className = 'project-card__readmore';
            btn.textContent = 'Read more';
            desc.appendChild(textNode);
            desc.appendChild(btn);

            btn.addEventListener('click', function (e) {
                e.stopPropagation();  // ← stops bubbling to card link/onclick
                e.preventDefault();   // ← stops any anchor default
                var expanded = desc.dataset.isExpanded === 'true';
                desc.childNodes[0].nodeValue = expanded ? desc.dataset.truncatedText : desc.dataset.fullText + ' ';
                btn.textContent = expanded ? 'Read more' : 'Show less';
                desc.dataset.isExpanded = expanded ? 'false' : 'true';
            });
        });
    }


    /* ════════════════════════════════════════
       6. PRICING — Card reveal + Billing toggle
       ════════════════════════════════════════ */

    function initPricingCards() {
        var cards = document.querySelectorAll('.pricing-card');
        if (!cards.length) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var index = Array.from(cards).indexOf(entry.target);
                setTimeout(function () {
                    entry.target.classList.add('visible');
                }, index * 120);
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.1 });

        cards.forEach(function (card) { observer.observe(card); });
    }

    function initBillingToggle() {
        var btn = document.getElementById('billingToggle');
        if (!btn) return;

        var isYearly = false;
        var priceEls = document.querySelectorAll('.price-main[data-monthly]');
        var originalEls = document.querySelectorAll('.price-original[data-monthly]');

        btn.addEventListener('click', function () {
            isYearly = !isYearly;
            btn.classList.toggle('is-on', isYearly);
            btn.setAttribute('aria-pressed', isYearly ? 'true' : 'false');

            priceEls.forEach(function (el) {
                el.textContent = isYearly ? el.getAttribute('data-yearly') : el.getAttribute('data-monthly');
            });
            originalEls.forEach(function (el) {
                el.textContent = isYearly ? el.getAttribute('data-yearly') : el.getAttribute('data-monthly');
            });
        });
    }

    // Global plan handler (called from inline onclick)
    window.handlePlan = function (planName) {
        alert('You selected the ' + planName + ' plan!');
    };


    /* ════════════════════════════════════════
       7. PROJECTS GATE MODAL (index.html)
       ════════════════════════════════════════ */

    function initProjectsModal() {
        var overlay = document.getElementById('projectsModalOverlay');
        var openBtn = document.getElementById('openProjectsModal');
        var closeBtn = document.getElementById('modalClose');
        var form = document.getElementById('projectsGateForm');
        if (!overlay || !openBtn || !form) return;

        function openModal() {
            overlay.classList.add('is-active');
            document.body.style.overflow = 'hidden';
            setTimeout(function () {
                var nameField = document.getElementById('gateName');
                if (nameField) nameField.focus();
            }, 300);
        }

        function closeModal() {
            overlay.classList.remove('is-active');
            document.body.style.overflow = '';
        }

        openBtn.addEventListener('click', openModal);

        document.querySelectorAll('.project-gate-trigger').forEach(function (link) {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                openModal();
            });
        });

        closeBtn.addEventListener('click', closeModal);
        overlay.addEventListener('click', function (e) { if (e.target === overlay) closeModal(); });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && overlay.classList.contains('is-active')) closeModal();
        });

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            var name = document.getElementById('gateName');
            var email = document.getElementById('gateEmail');
            var college = document.getElementById('gateCollege');
            var valid = true;

            [name, email, college].forEach(function (el) { el.classList.remove('has-error'); });

            if (!name.value.trim()) { name.classList.add('has-error'); valid = false; }
            if (!email.value.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
                email.classList.add('has-error'); valid = false;
            }
            if (!college.value.trim()) { college.classList.add('has-error'); valid = false; }
            if (!valid) return;

            var payload = {
                full_name: name.value.trim(),
                email: email.value.trim(),
                college_or_org: college.value.trim()
            };
            fetch('/gate/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
                body: JSON.stringify(payload)
            }).catch(function() {}).finally(function() {
                localStorage.setItem('ph-project-user', JSON.stringify({
                    name: payload.full_name, email: payload.email,
                    college: payload.college_or_org, timestamp: new Date().toISOString()
                }));
                window.location.href = '/projects/';
            });
        });
    }


    /* ════════════════════════════════════════
       8. CONTACT FORM (index.html)
       ════════════════════════════════════════ */

    function initContactForm() {
        var form = document.getElementById('contactForm');
        if (!form) return;

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            var name = document.getElementById('contactName');
            var email = document.getElementById('contactEmail');
            var message = document.getElementById('contactMessage');
            var btn = document.getElementById('contactSubmitBtn');
            var valid = true;

            [name, email, message].forEach(function (el) { el.classList.remove('has-error'); });

            if (!name.value.trim()) { name.classList.add('has-error'); valid = false; }
            if (!email.value.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
                email.classList.add('has-error'); valid = false;
            }
            if (!message.value.trim()) { message.classList.add('has-error'); valid = false; }
            if (!valid) return;

            btn.textContent = 'Sending…';
            btn.disabled = true;

            fetch('/contact/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
                body: JSON.stringify({full_name: name.value.trim(), email: email.value.trim(), message: message.value.trim()})
            }).then(function(r){return r.json();}).then(function(data){
                if (data.success) {
                    btn.textContent = '✓ Message Sent!';
                    btn.style.background = 'linear-gradient(135deg, #22c55e, #16a34a)';
                    setTimeout(function(){
                        form.reset();
                        btn.innerHTML = 'Send Message';
                        btn.style.background = ''; btn.disabled = false;
                    }, 3000);
                } else { btn.textContent = 'Send Message'; btn.style.background = ''; btn.disabled = false; }
            }).catch(function(){ btn.textContent = 'Send Message'; btn.style.background = ''; btn.disabled = false; });
        });
    }


    /* ════════════════════════════════════════
       9. SPLINE LAZY LOADER (index.html)
       ════════════════════════════════════════ */

    function initSplineSmart() {
        var wrapper = document.getElementById('spline-wrapper');
        var iframe = document.getElementById('spline-frame');
        var loader = document.getElementById('spline-loader');
        if (!wrapper || !iframe || !loader) return;

        var isLoaded = false;
        var minDisplayTime = 1500;
        var loadStartTime = Date.now();
        var auroraBg = document.querySelector('.aurora-bg');

        function hideLoader() {
            if (isLoaded) return;
            isLoaded = true;
            var remaining = Math.max(0, minDisplayTime - (Date.now() - loadStartTime));
            setTimeout(function () {
                loader.classList.add('is-hidden');
                // Resume aurora after Spline has settled
                setTimeout(function () {
                    if (loader && loader.parentNode) loader.parentNode.removeChild(loader);
                    if (auroraBg) auroraBg.style.animationPlayState = 'running';
                }, 700);
            }, remaining);
        }

        function loadSpline() {
            if (iframe.src || iframe.dataset.loaded) return;
            iframe.dataset.loaded = 'true';

            // Pause aurora while Spline WebGL initialises
            if (auroraBg) auroraBg.style.animationPlayState = 'paused';

            iframe.src = iframe.dataset.src;
            iframe.addEventListener('load', hideLoader);
            setTimeout(function () { if (!isLoaded) hideLoader(); }, 10000);

            // Watermark cover
            var splineCover = document.createElement('div');
            splineCover.id = 'spline-cover';
            splineCover.style.cssText = 'position:absolute;bottom:0;right:0;width:100%;height:57px;background:rgba(226.74188410194176,226.74188410194176,226.74188410194176, 1);z-index:5;pointer-events:none;';
            wrapper.appendChild(splineCover);
        }

        // Load only after user scrolls or clicks — not on idle
        // This gives the page time to paint and feel fast first
        var triggered = false;
        function triggerLoad() {
            if (triggered) return;
            triggered = true;
            // Small delay so the triggering interaction doesn't itself stutter
            setTimeout(loadSpline, 300);
            window.removeEventListener('scroll', triggerLoad);
            window.removeEventListener('click', triggerLoad);
            window.removeEventListener('touchstart', triggerLoad);
        }

        // Fallback: load after 4s even if user doesn't interact
        var fallbackTimer = setTimeout(function () {
            triggerLoad();
        }, 4000);

        window.addEventListener('scroll', triggerLoad, { passive: true });
        window.addEventListener('click', triggerLoad);
        window.addEventListener('touchstart', triggerLoad, { passive: true });
    }

    // ── Pause aurora when scrolled out of view ──
    function initAuroraPause() {
        var auroraBg = document.querySelector('.aurora-bg');
        if (!auroraBg) return;

        var scrollTimer;
        window.addEventListener('scroll', function () {
            auroraBg.style.animationPlayState = 'paused';
            clearTimeout(scrollTimer);
            scrollTimer = setTimeout(function () {
                auroraBg.style.animationPlayState = 'running';
            }, 150);
        }, { passive: true });
    }

    /* ════════════════════════════════════════
       10. WORKSHOP — Day cards + Feature items (workshop.html)
       ════════════════════════════════════════ */

    function initDayCards() {
        var cards = document.querySelectorAll('.day-card');
        if (!cards.length) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var index = Array.from(cards).indexOf(entry.target);
                setTimeout(function () {
                    entry.target.classList.add('visible');
                }, index * 120);
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.1 });

        cards.forEach(function (card) { observer.observe(card); });
    }

    function initFeatureItems() {
        var items = document.querySelectorAll('.feature-item');
        if (!items.length) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.1 });

        items.forEach(function (item) {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            observer.observe(item);
        });
    }


    /* ════════════════════════════════════════
       11. WORKSHOP SHARE CARD (workshop.html)
       ════════════════════════════════════════ */

    function initShareCard() {
        var overlay = document.getElementById('shareOverlay');
        var closeBtn = document.getElementById('shareClose');
        if (!overlay) return;

        function openShare(dayCard) {
            document.getElementById('shareDay').textContent = 'Day ' + dayCard.dataset.day;
            document.getElementById('shareTitle').textContent = dayCard.dataset.title;
            document.getElementById('shareDate').textContent = dayCard.dataset.date;
            document.getElementById('shareDesc').textContent = dayCard.dataset.desc;
            document.getElementById('shareOutcomeText').textContent = 'Outcome: ' + dayCard.dataset.outcome;
            overlay.classList.add('is-active');
            document.body.style.overflow = 'hidden';
        }

        function closeShare() {
            overlay.classList.remove('is-active');
            document.body.style.overflow = '';
        }

        document.querySelectorAll('.day-card__share-btn').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                openShare(btn.closest('.day-card'));
            });
        });

        closeBtn.addEventListener('click', closeShare);
        overlay.addEventListener('click', function (e) { if (e.target === overlay) closeShare(); });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && overlay.classList.contains('is-active')) closeShare();
        });

        // Copy link
        var copyBtn = document.getElementById('shareCopyLink');
        if (copyBtn) {
            copyBtn.addEventListener('click', function () {
                var day = document.getElementById('shareDay').textContent.replace('Day ', '');
                var url = window.location.origin + '/workshop-day.html?day=' + day;
                navigator.clipboard.writeText(url).then(function () {
                    copyBtn.textContent = '✓ Copied!';
                    setTimeout(function () {
                        copyBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy Link';
                    }, 2000);
                });
            });
        }

        // WhatsApp
        var waBtn = document.getElementById('shareWhatsApp');
        if (waBtn) {
            waBtn.addEventListener('click', function () {
                var title = document.getElementById('shareTitle').textContent;
                var day = document.getElementById('shareDay').textContent;
                var url = window.location.origin + '/workshop-day.html?day=' + day.replace('Day ', '');
                window.open('https://wa.me/?text=' + encodeURIComponent('🚀 Check out *' + day + ': ' + title + '* from the ProjectsHub AI Workshop!\n' + url), '_blank');
            });
        }

        // Twitter / X
        var twBtn = document.getElementById('shareTwitter');
        if (twBtn) {
            twBtn.addEventListener('click', function () {
                var title = document.getElementById('shareTitle').textContent;
                var day = document.getElementById('shareDay').textContent;
                var url = window.location.origin + '/workshop-day.html?day=' + day.replace('Day ', '');
                window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent('🚀 ' + day + ': ' + title + ' — ProjectsHub AI Workshop') + '&url=' + encodeURIComponent(url), '_blank');
            });
        }
    }


    /* ════════════════════════════════════════
       12. WORKSHOP DAY DETAIL (workshop-day.html)
       ════════════════════════════════════════ */

    function initWorkshopDay() {
        var container = document.getElementById('dayDetail');
        if (!container) return;

        var DAYS = {
            '1': {
                day: 'Day 1', title: 'Foundations of AI & Python for ML',
                date: 'Sunday, May 10 · 10 AM – 5 PM IST',
                desc: 'This opening day is all about building a rock-solid foundation. We start with a focused Python crash course tailored specifically for machine learning — covering essential syntax, data structures, and functional programming patterns you\'ll use daily. Then we dive deep into NumPy and Pandas, the backbone of every data pipeline, learning to manipulate, clean, and transform real-world datasets with confidence. By the afternoon, you\'ll be creating stunning visualizations with Matplotlib and Seaborn, and performing a complete Exploratory Data Analysis on a real dataset.',
                outcome: 'Complete EDA on a real dataset — cleaned, analyzed, and visualized.',
                outcomeDetail: 'You\'ll have a fully functional Jupyter notebook with a comprehensive analysis of a real-world dataset, including statistical summaries, correlation matrices, distribution plots, and actionable insights.',
                topics: [
                    { name: 'Python Crash Course for ML', sub: 'Lists, dicts, comprehensions, lambda functions, OOP basics' },
                    { name: 'NumPy & Pandas Deep Dive', sub: 'Array operations, DataFrames, groupby, merge, pivot tables' },
                    { name: 'Data Cleaning & Preprocessing', sub: 'Missing values, outliers, encoding, normalization' },
                    { name: 'Exploratory Data Analysis', sub: 'Statistical analysis, correlation, distribution analysis' },
                    { name: 'Matplotlib & Seaborn', sub: 'Line, bar, scatter, heatmaps, pair plots, styling' },
                    { name: 'ML Environment Setup', sub: 'Jupyter, Conda, Git, VS Code, project structure' }
                ]
            },
            '2': {
                day: 'Day 2', title: 'Machine Learning Models & Training',
                date: 'Monday, May 11 · 10 AM – 5 PM IST',
                desc: 'The most intensive day of the workshop. We jump straight into supervised learning — starting with linear and logistic regression, then moving to powerful ensemble methods like Random Forests and Gradient Boosting. You\'ll learn to properly evaluate models using precision, recall, F1, ROC-AUC, and cross-validation. The afternoon is dedicated to feature engineering and hyperparameter tuning with GridSearch and Optuna. By end of day, you\'ll have built and deployed a complete price prediction model.',
                outcome: 'Build a price prediction model with optimized hyperparameters.',
                outcomeDetail: 'A production-ready regression model trained on real estate data, complete with feature engineering pipeline, cross-validated metrics, and hyperparameter optimization — all in a reproducible notebook.',
                topics: [
                    { name: 'Linear & Logistic Regression', sub: 'Theory, implementation, regularization (L1/L2)' },
                    { name: 'Decision Trees & Random Forests', sub: 'Splitting criteria, pruning, ensemble methods' },
                    { name: 'Model Evaluation & Metrics', sub: 'Accuracy, precision, recall, F1, confusion matrix, ROC' },
                    { name: 'Hyperparameter Tuning', sub: 'GridSearchCV, RandomizedSearch, Optuna' },
                    { name: 'Cross-Validation Strategies', sub: 'K-Fold, Stratified, Leave-One-Out, time-series splits' },
                    { name: 'Feature Engineering', sub: 'Polynomial features, binning, target encoding, selection' }
                ]
            },
            '3': {
                day: 'Day 3', title: 'Deep Learning & Neural Networks',
                date: 'Tuesday, May 12 · 10 AM – 5 PM IST',
                desc: 'Today we unlock the power of deep learning. Starting from the mathematical foundations of neural networks — perceptrons, activation functions, backpropagation — we quickly move to building real models with TensorFlow and Keras. You\'ll implement convolutional neural networks (CNNs) for image classification and learn transfer learning with pre-trained models like ResNet and MobileNet. By end of day, you\'ll have an image classifier achieving 95%+ accuracy on a custom dataset.',
                outcome: 'Image classifier achieving 95%+ accuracy on a custom dataset.',
                outcomeDetail: 'A trained CNN model using transfer learning, with data augmentation, learning rate scheduling, and model checkpointing — exported and ready for inference.',
                topics: [
                    { name: 'Neural Network Architecture', sub: 'Perceptrons, layers, activation functions, backprop' },
                    { name: 'TensorFlow / Keras Basics', sub: 'Sequential API, functional API, callbacks, training loops' },
                    { name: 'Convolutional Neural Networks', sub: 'Conv layers, pooling, architecture patterns' },
                    { name: 'Transfer Learning', sub: 'ResNet, MobileNet, fine-tuning, feature extraction' },
                    { name: 'Image Classification Project', sub: 'Data augmentation, training, evaluation, visualization' },
                    { name: 'Model Saving & Optimization', sub: 'SavedModel, ONNX, quantization, TFLite' }
                ]
            },
            '4': {
                day: 'Day 4', title: 'Deployment & Real-World APIs',
                date: 'Wednesday, May 13 · 10 AM – 5 PM IST',
                desc: 'The final day brings everything together. You\'ll learn to wrap your ML models in production-grade FastAPI endpoints, containerize them with Docker, and deploy to the cloud. We cover CI/CD pipelines for automated model retraining, monitoring with logging and alerting, and best practices for ML in production. The capstone project ties all 4 days together — a complete end-to-end ML application from data to deployment.',
                outcome: 'Live deployed ML API accessible from anywhere.',
                outcomeDetail: 'A Dockerized FastAPI application serving your trained model, deployed on AWS/GCP with health checks, structured logging, and a CI/CD pipeline for automated deployments.',
                topics: [
                    { name: 'FastAPI for ML Serving', sub: 'Endpoints, Pydantic schemas, async handlers, file uploads' },
                    { name: 'Docker Containerization', sub: 'Dockerfile, multi-stage builds, docker-compose' },
                    { name: 'Cloud Deployment', sub: 'AWS EC2/Lambda, GCP Cloud Run, environment variables' },
                    { name: 'CI/CD for ML Pipelines', sub: 'GitHub Actions, automated testing, model versioning' },
                    { name: 'Monitoring & Logging', sub: 'Structured logs, health checks, alerting, metrics' },
                    { name: 'Capstone: End-to-End ML App', sub: 'Full pipeline from data ingestion to live API' }
                ]
            }
        };

        var params = new URLSearchParams(window.location.search);
        var dayNum = params.get('day') || '1';
        var data = DAYS[dayNum] || DAYS['1'];
        var prev = parseInt(dayNum) > 1 ? parseInt(dayNum) - 1 : null;
        var next = parseInt(dayNum) < 4 ? parseInt(dayNum) + 1 : null;

        document.title = data.day + ': ' + data.title + ' — ProjectsHub Workshop';

        var topicsHTML = data.topics.map(function (t, i) {
            return '<div class="topic-item"><div class="topic-item__icon">' + (i + 1) + '</div>' +
                '<div class="topic-item__text"><p class="topic-item__name">' + t.name + '</p>' +
                '<p class="topic-item__sub">' + t.sub + '</p></div></div>';
        }).join('');

        var navHTML = '<div class="day-detail__nav">';
        if (prev) navHTML += '<a href="/workshop-day.html?day=' + prev + '" class="day-nav-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="m12 19-7-7 7-7"/></svg> Day ' + prev + '</a>';
        else navHTML += '<span></span>';
        navHTML += '<a href="/workshop.html" class="day-nav-btn day-nav-btn--primary">Back to Workshop</a>';
        if (next) navHTML += '<a href="/workshop-day.html?day=' + next + '" class="day-nav-btn">Day ' + next + ' <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></a>';
        else navHTML += '<span></span>';
        navHTML += '</div>';

        container.innerHTML =
            '<div class="day-detail__badge"><span class="day-detail__badge-dot"></span> 4-Day AI Workshop</div>' +
            '<p class="day-detail__day">' + data.day + '</p>' +
            '<h1 class="day-detail__title">' + data.title + '</h1>' +
            '<p class="day-detail__date"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg> ' + data.date + '</p>' +
            '<p class="day-detail__desc">' + data.desc + '</p>' +
            '<h2 class="day-detail__section-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg> Topics Covered</h2>' +
            '<div class="day-detail__topics-grid">' + topicsHTML + '</div>' +
            '<div class="day-detail__outcome"><h3 class="day-detail__outcome-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> ' + data.outcome + '</h3><p class="day-detail__outcome-text">' + data.outcomeDetail + '</p></div>' +
            navHTML;
    }

// ADD this function (paste it just above the INIT comment block):
function initMarquee() {
    document.querySelectorAll('.marquee-track').forEach(function(track) {
        // Just set animation speed based on content width
        requestAnimationFrame(function() {
            var oneSetWidth = track.scrollWidth / 2;
            track.style.setProperty('--one-set-width', oneSetWidth + 'px');
        });
    });
}
/* ════════════════════════════════════════
   13 LOGO CLICK → Redirect to Home
   ════════════════════════════════════════ */

function initLogoRedirect() {
    var logo = document.querySelector('.logo');
    if (!logo) return;

    logo.style.cursor = 'pointer';

    logo.addEventListener('click', function () {
        window.location.href = '/';
    });
}
    /* ════════════════════════════════════════
       INIT — Run everything on DOMContentLoaded
       ════════════════════════════════════════ */

    function init() {
        // Shared across all pages
        initAuroraPause();
    initMarquee();  
        // index.html
        initPills();
        initStats();
        initCardTilt();
        initProjectCards();
        initReadMore();
        initPricingCards();
        initBillingToggle();
        initProjectsModal();
        initContactForm();
        initSplineSmart();
        initLogoRedirect();
        // projects.html
        initProjectFilter();

        // workshop.html
        initDayCards();
        initFeatureItems();
        initShareCard();

        // workshop-day.html
        initWorkshopDay();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
/* ── CSRF Cookie Helper ── */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
