# Template Fix Log — Admin Template & UI/UX Issues

Generated after implementing all Category 1 (Template Block Issues) and Category 2 (Admin UI/UX — template side) fixes from `admin-audit.md`.

---

## 1. `templates/admin/base.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | Line 1 | Separated `{% load i18n static %}` from `<!DOCTYPE html>` onto its own line. |
| 2 | `<head>` section | Removed hardcoded `<meta name="robots" content="NONE,NOARCHIVE">` (was duplicate — one here, one in `{% block blockbots %}`). Kept only the `{% block blockbots %}` version. |
| 3 | `<title>` tag | Removed ` | ProjectsHub` suffix from the base `<title>` tag. Now simply `{% block title %}{% endblock %}`. Ownership of the full page title is now in `base_site.html` (via its `{% block title %}` override) or in direct children of `base.html`. Eliminates double-branding. |
| 4 | CSS `<link>` order | Moved `{% block extrastyle %}{% endblock %}` to **after** `wp-admin.css` so child-injected override styles load after the base stylesheet (correct CSS cascade order). |
| 5 | `{% block blockbots %}` / `{% block extrahead %}` | Swapped order: `blockbots` (robots meta) now comes before `extrahead`, consistent with Django admin convention. |
| 6 | Sidebar `<ul id="adminmenu">` | Removed the duplicate consecutive `<li class="wp-menu-separator"></li>` (there were two adjacent ones before the Appearance section). |
| 7 | Footer area | Added `{% block extra_js %}{% endblock %}` immediately after `{% block footer %}{% endblock %}` to provide a clean, documented hook for child templates to inject scripts after `wp-admin.js`. |

---

## 2. `templates/admin/base_site.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | `{% block title %}` | No change to the block content itself. The fix is upstream in `base.html` (the base `<title>` tag no longer appends `| ProjectsHub`), so `base_site.html`'s title now renders correctly as `[subtitle | ]title | ProjectsHub Admin` without double-branding. |

---

## 3. `templates/admin/index.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | Line 4 `{% block title %}` | Changed from `Dashboard | ProjectsHub` to `Dashboard`. The `base_site.html` chain now appends `| ProjectsHub Admin` correctly, yielding `Dashboard | ProjectsHub Admin` without duplication. |

---

## 4. `templates/admin/backup.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | `{% block title %}` | Updated from `Database Backup & Export Manager | ProjectsHub` to `Database Backup & Export Manager | ProjectsHub Admin` (extends `base.html` directly, so must own the full title). |
| 2 | After `{% block content_title %}` | Added `{% block breadcrumbs %}` block with `Dashboard › Backup & Export` breadcrumb trail. |

---

## 5. `templates/admin/guide.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | `{% block title %}` | Updated from `Master Project Guide & Operations Manual | ProjectsHub` to `...| ProjectsHub Admin`. |
| 2 | After `{% block content_title %}` | Added `{% block breadcrumbs %}` block with `Dashboard › Project Guide` breadcrumb trail. |

---

## 6. `templates/admin/live_chat.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | `{% block title %}` | Changed from `Live Chat` to `Live Chat | ProjectsHub Admin` (extends `base.html` directly, needs full title). |
| 2 | After `{% block content_title %}` | Added `{% block breadcrumbs %}` block with `Dashboard › Live Chat` breadcrumb trail. |

---

## 7. `templates/admin/seo_dashboard.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | Line 2 `{% load %}` | Changed `{% load static %}` to `{% load i18n static %}` — added missing `i18n` load tag for consistency with all other admin templates. |
| 2 | `{% block title %}` | Changed from `SEO Dashboard` to `SEO Dashboard | ProjectsHub Admin`. |
| 3 | After `{% block content_title %}` | Added `{% block breadcrumbs %}` block with `Dashboard › SEO Dashboard` breadcrumb trail. |

---

## 8. `templates/admin/settings.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | `{% block title %}` | Changed from `Settings | ProjectsHub` to `Settings | ProjectsHub Admin`. |
| 2 | After `{% block bodyclass %}` | Added `{% block breadcrumbs %}` block with `Dashboard › Settings` breadcrumb trail. |

---

## 9. `templates/admin/nav_menus.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | `{% block title %}` | Changed from `Menus | ProjectsHub` to `Menus | ProjectsHub Admin`. |
| 2 | After `{% block bodyclass %}` | Added `{% block breadcrumbs %}` block with `Dashboard › Appearance › Menus` breadcrumb trail. |

---

## 10. `templates/admin/plugins.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | `{% block title %}` | Changed from `Plugins | ProjectsHub` to `Plugins | ProjectsHub Admin`. |
| 2 | After `{% block bodyclass %}` | Added `{% block breadcrumbs %}` block with `Dashboard › Plugins` breadcrumb trail. |

---

## 11. `templates/admin/core/assets_manager.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | `{% block title %}` | Changed from `Media & Storage Assets Manager | ProjectsHub` to `...| ProjectsHub Admin`. |
| 2 | After `{% block content_title %}` | Added `{% block breadcrumbs %}` block with `Dashboard › Media & Assets` breadcrumb trail. |

---

## 12. `templates/admin/change_form.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | Category meta box — required pill | Replaced `{% if adminform.form.category_ref.field.required or adminform.form.category.field.required %}` with safe guarded checks: first tests `'category_ref' in adminform.form.fields` before accessing `.field.required`, then tests `'category' in adminform.form.fields`. Prevents `KeyError`/`AttributeError` 500 errors on models that have only one of the two fields. |
| 2 | Featured Image meta box — required pill | Same fix pattern: replaced `{% if adminform.form.image.field.required or adminform.form.thumbnail.field.required %}` with sequential guarded checks using `in adminform.form.fields` before accessing `.field.required`. |

---

## 13. `templates/admin/includes/fieldset.html`

| # | Lines affected | Change |
|---|---|---|
| 1 | Lines 9–14 (field suppression conditions) | Replaced substring `in "title,slug,..."` string checks with explicit per-value equality comparisons (`fname == 'title'`, `fname == 'slug'`, etc.) using a `{% with fname=field.field.name %}` variable. Eliminates the substring-match bug where field names like `"or"`, `"e"`, `"le"` (substrings of the suppression list strings) would be incorrectly suppressed. |

---

## Verification

```
$ d:\HarshQA\.venv\Scripts\python.exe d:\HarshQA\manage.py check
System check identified no issues (0 silenced).
```

All changes verified. No Django system-level errors introduced.
