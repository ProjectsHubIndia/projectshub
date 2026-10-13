# Fix Log — Admin.py & Views.py (Categories 3 & 4)

Generated after implementing all Category 3 (Django Admin Class Issues) and Category 4 (Custom Admin Views/URLs) fixes from `admin-audit.md`.

---

## Verification

```
$ d:\HarshQA\.venv\Scripts\python.exe d:\HarshQA\manage.py check
System check identified no issues (0 silenced).
```

All changes verified. No Django system-level errors introduced.

---

## Changes to `core/admin.py`

### 1. `SiteSettingsAdmin` — Added `readonly_fields` and `active_theme` fieldset

**Problem:** `created_at` and `updated_at` are `auto_now_add`/`auto_now` fields — without `readonly_fields` they silently disappear from the change form. The `active_theme` field existed on the model but was absent from every fieldset, making it invisible to admins.

**Fix:**
- Added `readonly_fields = ('created_at', 'updated_at')` to the class.
- Added an `Appearance` fieldset exposing `active_theme`.
- Added a collapsed `Record Info` fieldset showing `created_at` and `updated_at`.

---

### 2. `WorkshopCardAdmin` — Added `fieldsets`, `list_filter`, `search_fields`, and `readonly_fields`

**Problem:** `WorkshopCardAdmin` had no `fieldsets` (flat unstyled form), no `list_filter`, no `search_fields`, and no `readonly_fields` for the `created_at` auto field.

**Fix:**
- Added `list_filter = ('is_active', 'is_featured')`.
- Added `search_fields = ('title', 'subtitle', 'description')`.
- Added `readonly_fields = ('created_at',)`.
- Added structured `fieldsets`:
  - Workshop Details (title, subtitle, description)
  - Schedule & Logistics (date, time, mode, seats)
  - Pricing & Enrollment (price, price_label, enroll_url)
  - Visibility & Ordering (is_active, is_featured, order)
  - Record Info (created_at, collapsed)

---

### 3. `WorkshopEnrollmentAdmin` — Added `readonly_fields`

**Problem:** `created_at` is `auto_now_add` — without `readonly_fields` it doesn't appear in the change form.

**Fix:** Added `readonly_fields = ('created_at',)`.

---

### 4. `IdeaSubmissionAdmin` — Added `readonly_fields`

**Problem:** `created_at` is `auto_now_add` — without `readonly_fields` it doesn't appear in the change form.

**Fix:** Added `readonly_fields = ('created_at',)`.

---

### 5. `BlogPostAdmin` — Added `readonly_fields` and `fieldsets`

**Problem:** `created_at` and `updated_at` are auto fields and were missing from `readonly_fields`, so they never appeared in the change form. There were also no `fieldsets` defined — all fields rendered as a flat unstyled list.

**Fix:**
- Added `readonly_fields = ('created_at', 'updated_at')`.
- Added structured `fieldsets`:
  - Content (title, slug, category, category_ref, tags, excerpt, lead, content)
  - Visuals (emoji, gradient colours, featured_image, image, image_url)
  - Publishing (author info, read_time, published_at, visibility flags, order)
  - Record Info (created_at, updated_at, collapsed)

---

### 6. `PageAdmin.duplicate_page` — Added slug uniqueness check

**Problem:** The action set `p.slug = f"{p.slug}-copy"` unconditionally. If a page with that slug already existed (e.g. from a previous duplicate), it raised `IntegrityError` due to the unique constraint on `slug`.

**Fix:** Replaced the direct slug assignment with a uniqueness-checking loop identical to the pattern used in `ProjectAdmin.duplicate_project`:
```python
base_slug = f"{orig_slug}-copy"
new_slug = base_slug
idx = 1
while Page.objects.filter(slug=new_slug).exists():
    new_slug = f"{base_slug}-{idx}"
    idx += 1
p.slug = new_slug
```
Also saved `orig_title` before nulling `pk` to avoid operating on a modified object mid-loop.

---

## Changes to `core/views.py`

### 7. `admin_settings_view` — Replaced fake success messages on non-persistent tabs

**Problem:** The Writing, Reading, and Permalinks tabs called `messages.success(request, "... saved.")` without writing anything to the database. The UI showed a green "Saved" toast even though nothing was persisted — actively misleading users.

**Fix:** Replaced `messages.success(...)` with `messages.info(...)` on those three tabs, with honest copy:
- Writing tab: `"Writing settings are informational only and are managed in code. No changes were saved."`
- Reading tab: `"Reading settings are informational only and are managed in code. No changes were saved."`
- Permalinks tab: `"Permalink settings are informational only and are managed in code. No changes were saved."`

Also added an explicit `elif active_tab == 'permalinks':` branch (previously only the first three `elif` ran; `permalinks` fell through silently with no message at all when navigating away then back).

The General and Analytics tabs still call `messages.success(...)` and persist data correctly — no change there.

---

## Files Changed

| File | Lines changed |
|---|---|
| `core/admin.py` | SiteSettingsAdmin (~130–160), WorkshopCardAdmin (~920–940), WorkshopEnrollmentAdmin (~950), IdeaSubmissionAdmin (~870), BlogPostAdmin (~680–720), PageAdmin.duplicate_page (~1460–1475) |
| `core/views.py` | `admin_settings_view` POST handler (~2197–2212) |

## Files NOT changed

- `core/urls.py` — all custom admin URL wiring was already correct per the audit (verified ✓).
- `projectshub/urls.py` — all custom admin paths were already correctly ordered before `admin.site.urls` per the audit (verified ✓).
- `core/seo_views.py` — `admin_seo_run_audit` and `admin_seo_dashboard` were confirmed `@staff_member_required` (verified ✓).
- `core/chat_views.py` — `admin_live_chat_view` was confirmed `@staff_member_required` (verified ✓).
