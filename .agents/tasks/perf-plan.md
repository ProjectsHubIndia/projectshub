# Frontend Performance Optimization Plan

**Current State**: Lighthouse Performance score 25/100
**Target**: 90+ Performance score
**Key Issues**: Render-blocking CSS (410ms), high JS execution time (2.0s), TBT 950ms, unused CSS/JS

---

## Implementation Plan

### Phase 1: Eliminate Render-Blocking CSS (FEAT-001)

- [ ] 1. **Install and configure django-compressor**
      - Add `django-compressor==4.5.1` to `requirements.txt`
      - Install via `pip install django-compressor`
      - Configure in `projectshub/settings.py`:
        * Add `'compressor'` to `INSTALLED_APPS` (after staticfiles)
        * Add `'compressor.finders.CompressorFinder'` to `STATICFILES_FINDERS`
        * Set `COMPRESS_ENABLED=True`, `COMPRESS_OFFLINE=True`
        * Configure CSS/JS filters for minification
      Files: `requirements.txt`, `projectshub/settings.py`
      Verify: `python manage.py collectstatic --noinput && python manage.py compress` runs successfully

- [ ] 2. **Extract and inline critical CSS**
      - Create `static/css/critical.css` with above-the-fold styles from:
        * CSS variables/root declarations from bundle.min.css
        * Reset styles, html/body base styles
        * Navbar component styles
        * Hero section styles
        * Basic typography and layout utilities
      - Inline critical.css content directly in `templates/core/base.html` <head>
      Files: `static/css/critical.css`, `templates/core/base.html`
      Verify: Visit http://127.0.0.1:8000/ - navbar and hero render without FOUC

- [ ] 3. **Defer non-critical CSS**
      - In `templates/core/base.html`, apply media=print onload trick to:
        * `bundle.min.css` link tag
        * `modern-design-system.css` link tag
        * Move Bootstrap CDN link to bottom before </body> with same technique
      - Wrap deferred CSS links with `{% compress css %}` tags
      Files: `templates/core/base.html`
      Verify: DevTools Network tab shows CSS not blocking rendering; all pages render correctly

---

### Phase 2: Reduce CSS Bloat (FEAT-002)

- [ ] 4. **Extract inline styles from templates**
      - Extract `<style>` blocks from these templates into external files:
        * `case_studies.html` → `static/css/case_studies.css`
        * `error404.html` → `static/css/error404.css`
        * `page_detail.html` → `static/css/page_detail.css`
        * `privacy.html`, `refund.html`, `terms.html` → `static/css/legal-pages.css` (shared)
        * `sitemap.html` → `static/css/sitemap.css`
        * `AI_roadmap.html` → append to `static/css/ai_roadmap.css`
        * `workshop.html` → append to `static/css/workshop.css`
        * `workshop-day.html` → append to `static/css/workshop-day.css`
      Files: 9 template files, 7 new/updated CSS files
      Verify: Visit all affected pages, verify styles render correctly

- [ ] 5. **Compress per-page CSS**
      - Update all templates using `{% block extra_css %}` to wrap CSS links with `{% compress css %}` tags
      - Ensure `{% load compress %}` is at top of each template using compression
      Files: All templates in `templates/core/` directory
      Verify: `python manage.py compress` generates compressed CSS bundles in `staticfiles/CACHE/`

- [ ] 6. **Remove duplicate CSS rules**
      - Audit `bundle.min.css` for duplicates with `modern-design-system.css`
      - Remove duplicate navbar, typography, button styles from bundle.min.css
      Files: `static/css/bundle.min.css`
      Verify: No visual regressions on any page; CSS size reduced

---

### Phase 3: Optimize JavaScript (FEAT-003)

- [ ] 7. **Compress global JavaScript**
      - Wrap all `<script>` tags in `templates/core/base.html` with `{% compress js %}` tags:
        * Bootstrap bundle.min.js
        * cookie-consent.js
        * live-chat.js
        * script.js
        * idea-modal.js
      - Preserve `defer` attributes on all script tags
      Files: `templates/core/base.html`
      Verify: Scripts load and execute correctly; no console errors

- [ ] 8. **Conditionally load per-page JavaScript**
      - Move `ai-chatbot.js` from global to conditional loading in:
        * `project_detail.html` via `{% block extra_js %}`
        * `workshop.html` via `{% block extra_js %}`
      - Move `ai_roadmap.js` to load only on `/ai-roadmap/` page
      - Move `social-share.js` to load only on pages with share buttons
      Files: Multiple template files
      Verify: Test affected pages; all interactive features work

- [ ] 9. **Document unused JavaScript**
      - Audit `static/js/` files against template usage
      - Create `static/js/UNUSED.md` documenting candidates for removal:
        * `wp-admin.js` (81 bytes)
        * `wp-acf-blocks.js` (33KB) - if WordPress not used
      - Do NOT delete files yet, only document
      Files: `static/js/UNUSED.md`
      Verify: Documentation is accurate

---

### Phase 4: Production Optimization (FEAT-004)

- [ ] 10. **Enable Brotli compression**
      - Add `brotli==1.1.0` to `requirements.txt` and install
      - Configure `COMPRESS_STORAGE` in `projectshub/settings.py` for Brotli support
      Files: `requirements.txt`, `projectshub/settings.py`
      Verify: `staticfiles/CACHE/` contains both .gz and .br files

- [ ] 11. **Optimize resource hints**
      - Verify preconnect hints in `templates/core/base.html`:
        * fonts.googleapis.com (present)
        * fonts.gstatic.com (present)
        * cdn.jsdelivr.net (present)
      - All external resources have appropriate preconnect/dns-prefetch hints
      Files: `templates/core/base.html`
      Verify: Visual inspection of <head> section

- [ ] 12. **Configure production compression settings**
      - In `projectshub/settings.py`, set:
        * `COMPRESS_OUTPUT_DIR='CACHE'`
        * `COMPRESS_CSS_HASHING_METHOD='content'`
        * `COMPRESS_OFFLINE_CONTEXT={'STATIC_URL': settings.STATIC_URL}`
        * `COMPRESS_OFFLINE=True` (production only)
      Files: `projectshub/settings.py`
      Verify: `python manage.py collectstatic && python manage.py compress` succeeds

- [ ] 13. **Update deployment documentation**
      - Update `README.md` deployment section:
        * Add step: `python manage.py compress` after collectstatic
        * Document performance optimizations applied
      - Create `.agents/tasks/perf-optimization/performance-checklist.md`
      Files: `README.md`, new checklist file
      Verify: Documentation is clear and accurate

- [ ] 14. **Verify production performance**
      - Deploy to Railway production URL
      - Run Lighthouse audit on production URL
      - Verify Performance score ≥ 80 (target 90+)
      - Verify Core Web Vitals:
        * FCP < 1.5s (was 3.5s)
        * LCP < 2.5s (was 3.9s)
        * TBT < 200ms (was 950ms)
      Files: N/A
      Verify: Lighthouse audit results

---

## Verification Commands

```bash
# After each phase
python manage.py collectstatic --noinput
python manage.py compress
python manage.py runserver

# Test suite
python manage.py test

# Production deployment
python manage.py collectstatic --noinput
python manage.py compress
gunicorn projectshub.wsgi:application
```

---

## Expected Outcomes

- **Performance Score**: 25 → 90+
- **First Contentful Paint**: 3.5s → <1.5s
- **Largest Contentful Paint**: 3.9s → <2.5s
- **Total Blocking Time**: 950ms → <200ms
- **CSS Size**: ~1.1MB → ~700KB (compressed)
- **JS Size**: ~400KB → ~280KB (compressed)
- **Render-blocking**: 410ms → 0ms

---

## Dependencies Already Present

✅ WhiteNoise installed and configured
✅ CompressedStaticFilesStorage enabled
✅ All JS uses `defer` attribute
✅ Some CSS uses media=print onload pattern
✅ Google Fonts preloaded
✅ External resource preconnect hints present

## Dependencies to Add

❌ django-compressor (for CSS/JS bundling and minification)
❌ brotli (for Brotli compression support)
