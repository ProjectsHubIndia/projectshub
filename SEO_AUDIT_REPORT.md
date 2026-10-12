# ProjectsHub — SEO & Security Audit (Stage A) — 12 Oct 2026

Scope: the existing Django 4.2 site in this repo (single `core` app, SQLite locally / Postgres via
`DATABASE_URL`, deployed on cPanel Passenger, Railway and Vercel). Audited against the
"SEO Ranking Checker / SEO Automation" master brief, Phase 1.

Verification: `manage.py check` clean, no pending migrations, **71/71 tests pass**
(58 existing + 13 new in `core/tests/test_seo_fixes.py`). Rendered pages were checked against a
*copy* of `db.sqlite3`; the real database was not modified.

## 1. Fixed in this pass

| # | Severity | Issue (evidence) | Fix | Files |
|---|---|---|---|---|
| 1 | Critical | Canonical tags, og:url, JSON-LD, `robots.txt` and `sitemap.xml` were built from the request Host. On `projectshub-production.up.railway.app` the whole site declared itself canonical and its sitemap listed Railway URLs — a full duplicate of the site competing with projectshub.co.in. | New `CANONICAL_SITE_URL` setting (= `SITE_URL` or `https://SITE_DOMAIN`); `get_base_url()` and the template `site_url` now always use it. Platform hosts (`*.railway.app`, `*.vercel.app`) get `X-Robots-Tag: noindex, nofollow`. | settings.py, seo.py, context_processors.py, middleware.py |
| 2 | Critical | Every project had two indexable URLs (`/projects/8/` and `/projects/<slug>/`). Canonical pointed to the numeric URL while the sitemap listed the slug URL (conflicting signals). | Numeric URLs 301 to the slug URL (query string kept). Canonical, og:url, breadcrumbs, ItemList and related-project links use `get_absolute_url()`. | views.py, project_detail.html, projects.html |
| 3 | High | Sitemap listed `/services/`, which 301-redirects; it never checked redirects or noindex flags. Workshop pages were missing. | Sitemap now skips active redirect sources and SEOData rows that are noindex, de-duplicates, and adds workshop + day pages. | views.py |
| 4 | High | Homepage canonical contained a newline (`https://…/\n`). | Template fixed. | index.html |
| 5 | High | JSON-LD from `seo.py` was output with `|safe` using plain `json.dumps` — a title containing `</script>` could break out of the script tag (stored XSS via admin content). | `safe_json_ld()` escapes `< > &`. | seo.py |
| 6 | High | Any staff user could use `/admin/api/quick-edit/` on *any* model in *any* app (e.g. deactivate a superuser via `auth.user`). | Restricted to `core` models and the matching `change_<model>` permission; errors no longer echo exception text. | views.py |
| 7 | Medium | Rate limits keyed on the first `X-Forwarded-For` value, which clients can spoof. | `get_client_ip()` uses the hop added by the trusted proxy (`TRUSTED_PROXY_COUNT`, default 1 in production, 0 locally). | settings.py, views.py |
| 8 | Medium | `/api/chatbot/lead/` had no rate limit or length limits (each call creates a CRM inquiry); chatbot endpoints returned raw exception text. | 5 leads/IP/hour, field length caps, generic error messages. | views.py |
| 9 | Medium | Redirect manager accepted self-redirects, chains and loops. | `Redirect.clean()` rejects off-site/protocol-relative targets, self-redirects, loops and chains (admin form validation; no migration). | models.py |
| 10 | Medium | AI Roadmap title/description showed `?` instead of `—` (encoding damage) in search snippets. | Restored. | AI_roadmap.html |
| 11 | Medium | Project meta descriptions contained raw Markdown (`**LLM-Powered…`). | `clean_description()` strips HTML/Markdown and trims at a word boundary. | seo.py, project_detail.html, views.py |
| 12 | Low | 7 JSON-LD `logo` URLs pointed to files that don't exist (`favicon_io/logo.png`, `image/logo.png`). | Point to `image/logo/projectshub-logo-dark.png`. | 6 templates |
| 13 | Low | Project `og:image` block was wrapped in `{% if %}` outside a block (ignored by Django), so projects without an image emitted an empty og:image; image URLs were relative. | Fallback to default image; absolute URLs. | project_detail.html |
| 14 | Low | BlogPosting could emit `"datePublished": ""`. | Dates omitted when absent. | seo.py |

## 2. Needs your decision (not changed)

1. **SEOData admin edits mostly don't reach the page.** Most templates hard-code `{% block title %}`/description, which override `SEOData`. But the existing SEOData rows were auto-generated and are inconsistent with the pages (e.g. `/workshop/` row says "3-Day", page says "5-Day"; `/ai-roadmap/` row has the generic site title). Making SEOData win today would *worsen* live titles. Recommended: add an explicit "override template metadata" flag (additive migration) and review the 12 rows first.
2. **Thin/test content is live and in the sitemap:** project `/projects/test/` (title and description "test"). Unpublish it in admin.
3. **Unverifiable claims in metadata/schema:** "50+ projects" (8 in DB), hard-coded `Course` price ₹999, Organization `sameAs` profiles. Confirm or remove.
4. Redirect row `/admin → /admin/` is redundant (middleware handles it) and will now fail validation if re-saved; safe to deactivate.
5. On cPanel, set `ENVIRONMENT=production` (and `SECRET_KEY`) so `DEBUG` defaults off and production defaults apply.

## 3. What already exists vs. the master brief

Present: per-path SEOData overrides, auto meta/OG/Twitter/JSON-LD engine (`core/seo.py`), robots.txt, sitemap.xml, llms.txt, DB redirect manager + middleware, custom 404/500, management commands (`audit_content`, `audit_images`, `audit_links`, `crawl_existing_site`, `generate_seo_report`), security headers/CSP, admin RBAC via Django groups.

Not present (Phases 2–17): SEO dashboard sections, keyword research, rank tracking, Search Console / Analytics / Google Ads OAuth, background job runner, crawler with SSRF guards, scoring engine, content workspace, internal-link graph, backlinks, reports (PDF), audit log, encrypted credential storage.

Key architecture constraints for those phases:
- **No background worker** on cPanel shared hosting. Crawls and rank checks must run from cron → management commands (not inside web requests).
- **Real data requires paid/authorised providers**: a SERP API (e.g. DataForSEO, SerpApi) for rankings, Google Ads API developer token for Keyword Planner, Google Cloud OAuth client for Search Console/Analytics. Without them the UI must show "integration required", never estimates.
- Locmem cache is per-process; rate limits/quotas need a DB- or Redis-backed cache once several workers run.

## 4. Proposed next stages

- **B** — Models/migrations: SEOProject, Keyword, RankObservation, CrawlJob, CrawlFinding, IntegrationCredential (encrypted), ApiUsage, AuditLog; permissions.
- **C** — Crawler (cron command, SSRF-safe, robots-aware, resumable) + technical audit findings & explainable score in admin.
- **D** — SEOData override flag + snippet preview, sitemap index/split, 404 logging, redirect chain report.
- **E/F** — Search Console OAuth (read-only scope first), then SERP provider rank tracking.
- **G–J** — content/internal links, optional Ads/backlinks, CSV/PDF reports, deployment checklist.
