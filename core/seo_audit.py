"""
core/seo_audit.py — technical SEO audit for the admin SEO dashboard.

Every URL in /sitemap.xml is rendered in-process (no external requests) and checked for
the things search engines actually read: HTTP status, indexability, title, meta
description, canonical, H1, structured data, social tags, image alt text and content
length. Site-level checks cover robots.txt, the sitemap and the redirect table.

The score is an explainable internal checklist score — it is NOT a Google metric and
does not predict rankings. Search performance data (clicks, impressions, positions)
requires connecting Google Search Console; nothing here is estimated or invented.
"""
import csv
import io
import json
import re
import time
from collections import defaultdict
from html.parser import HTMLParser
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import Client
from django.utils import timezone

CACHE_KEY = 'ph_seo_audit_v1'
CACHE_SECONDS = 60 * 60
MAX_URLS = 300

TITLE_MIN, TITLE_MAX = 30, 60
DESC_MIN, DESC_MAX = 70, 160
THIN_WORDS = 250

SEVERITY_WEIGHT = {'critical': 25, 'warning': 8, 'notice': 2}


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self._in_title = False
        self.meta = {}
        self.links = defaultdict(list)
        self.h1 = 0
        self.h1_text = []
        self._in_h1 = False
        self.imgs = 0
        self.imgs_no_alt = 0
        self.jsonld = []
        self._in_jsonld = False
        self._buf = []
        self._skip = 0
        self.text = []
        self.lang = None
        self._in_body = False

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or '') for k, v in attrs}
        if tag == 'html':
            self.lang = a.get('lang')
        elif tag == 'body':
            self._in_body = True
        elif tag == 'title' and self.title is None:
            self._in_title = True
            self._buf = []
        elif tag == 'meta':
            key = (a.get('name') or a.get('property') or '').lower()
            if key and key not in self.meta:
                self.meta[key] = a.get('content', '')
        elif tag == 'link':
            rel = a.get('rel', '').lower()
            if rel:
                self.links[rel].append(a.get('href', ''))
        elif tag == 'h1':
            self.h1 += 1
            self._in_h1 = True
        elif tag == 'img':
            self.imgs += 1
            if 'alt' not in a:
                self.imgs_no_alt += 1
        elif tag == 'script':
            if a.get('type', '').lower() == 'application/ld+json':
                self._in_jsonld = True
                self._buf = []
            else:
                self._skip += 1
        elif tag in ('style', 'noscript', 'svg'):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag == 'title' and self._in_title:
            self.title = ''.join(self._buf).strip()
            self._in_title = False
        elif tag == 'h1':
            self._in_h1 = False
        elif tag == 'script':
            if self._in_jsonld:
                self.jsonld.append(''.join(self._buf))
                self._in_jsonld = False
            elif self._skip:
                self._skip -= 1
        elif tag in ('style', 'noscript', 'svg') and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._in_title or self._in_jsonld:
            self._buf.append(data)
            return
        if self._in_h1:
            self.h1_text.append(data.strip())
        if self._in_body and not self._skip:
            self.text.append(data)


def _issue(severity, check, message, fix):
    return {'severity': severity, 'check': check, 'message': message, 'fix': fix}


def canonical_base():
    return (getattr(settings, 'CANONICAL_SITE_URL', '') or 'https://projectshub.co.in').rstrip('/')


def _client():
    host = urlparse(canonical_base()).netloc or 'projectshub.co.in'
    return _HttpsClient(HTTP_HOST=host), host


class _HttpsClient(Client):
    """In-process client whose requests are always HTTPS (like real visitors on the canonical domain)."""
    def generic(self, *args, secure=True, **kwargs):
        return super().generic(*args, secure=True, **kwargs)


def sitemap_paths(client):
    res = client.get('/sitemap.xml')
    if res.status_code != 200:
        return [], res.status_code
    locs = re.findall(r'<loc>(.*?)</loc>', res.content.decode('utf-8', 'ignore'))
    base = canonical_base()
    paths = []
    for loc in locs:
        loc = loc.replace('&amp;', '&')
        paths.append(loc[len(base):] or '/' if loc.startswith(base) else urlparse(loc).path or '/')
    return paths[:MAX_URLS], 200


def audit_page(client, path):
    started = time.monotonic()
    res = client.get(path)
    elapsed_ms = int((time.monotonic() - started) * 1000)
    page = {'path': path, 'status': res.status_code, 'ms': elapsed_ms, 'issues': []}
    issues = page['issues']

    if res.status_code in (301, 302, 307, 308):
        issues.append(_issue('critical', 'Status', f"Redirects ({res.status_code}) to {res.get('Location', '?')}",
                             'Remove redirected URLs from the sitemap, or point the redirect elsewhere.'))
        return _finish(page)
    if res.status_code != 200:
        issues.append(_issue('critical', 'Status', f'Returns HTTP {res.status_code}',
                             'Fix the page or remove it from the sitemap.'))
        return _finish(page)
    if 'html' not in res.get('Content-Type', ''):
        return _finish(page)

    p = _PageParser()
    try:
        p.feed(res.content.decode('utf-8', 'ignore'))
    except Exception:
        pass

    title = (p.title or '').strip()
    desc = (p.meta.get('description') or '').strip()
    robots = (p.meta.get('robots') or '').lower()
    x_robots = (res.get('X-Robots-Tag') or '').lower()
    canonicals = [c for c in p.links.get('canonical', []) if c]
    canonical = canonicals[0].strip() if canonicals else ''
    expected = canonical_base() + path
    words = len(re.findall(r'\w+', ' '.join(p.text)))

    page.update({
        'title': title, 'title_len': len(title), 'description': desc, 'desc_len': len(desc),
        'canonical': canonical, 'robots': robots or 'index, follow (default)', 'h1': p.h1,
        'h1_text': ' '.join(t for t in p.h1_text if t)[:120], 'words': words, 'images': p.imgs,
        'images_no_alt': p.imgs_no_alt, 'og_image': p.meta.get('og:image', ''), 'lang': p.lang or '',
        'schema_types': [],
    })

    # Indexability
    if 'noindex' in robots or 'noindex' in x_robots:
        issues.append(_issue('critical', 'Indexability', 'Page is set to noindex but is listed in the sitemap.',
                             'Remove the noindex directive, or exclude the page from the sitemap.'))
    # Title
    if not title:
        issues.append(_issue('critical', 'Title', 'Missing <title>.', 'Add a unique, descriptive title.'))
    elif len(title) < TITLE_MIN:
        issues.append(_issue('warning', 'Title', f'Title is short ({len(title)} chars).',
                             f'Aim for roughly {TITLE_MIN}–{TITLE_MAX} characters describing the page.'))
    elif len(title) > TITLE_MAX + 10:
        issues.append(_issue('warning', 'Title', f'Title is long ({len(title)} chars) and may be cut off in results.',
                             f'Keep the important words within ~{TITLE_MAX} characters.'))
    # Description
    if not desc:
        issues.append(_issue('warning', 'Meta description', 'Missing meta description.',
                             'Write a 70–160 character summary; search engines may use it as the snippet.'))
    elif len(desc) < DESC_MIN:
        issues.append(_issue('notice', 'Meta description', f'Description is short ({len(desc)} chars).',
                             f'Expand to roughly {DESC_MIN}–{DESC_MAX} characters.'))
    elif len(desc) > DESC_MAX + 20:
        issues.append(_issue('notice', 'Meta description', f'Description is long ({len(desc)} chars).',
                             f'Trim to about {DESC_MAX} characters.'))
    # Canonical
    if not canonical:
        issues.append(_issue('warning', 'Canonical', 'No canonical link.', 'Add <link rel="canonical"> pointing to this URL.'))
    elif len(canonicals) > 1:
        issues.append(_issue('warning', 'Canonical', f'{len(canonicals)} canonical tags found.', 'Keep exactly one canonical tag.'))
    elif canonical.rstrip('/') != expected.rstrip('/'):
        issues.append(_issue('critical', 'Canonical', f'Canonical points to {canonical} instead of this URL.',
                             'Make the canonical match the sitemap URL (or remove this URL from the sitemap).'))
    # Headings
    if p.h1 == 0:
        issues.append(_issue('warning', 'Headings', 'No H1 heading.', 'Add one H1 that states the page topic.'))
    elif p.h1 > 1:
        issues.append(_issue('notice', 'Headings', f'{p.h1} H1 headings.', 'Use a single H1; demote the others to H2.'))
    # Structured data
    for block in p.jsonld:
        try:
            data = json.loads(block)
        except ValueError:
            issues.append(_issue('warning', 'Structured data', 'A JSON-LD block is not valid JSON.',
                                 'Fix the syntax (validate with Google’s Rich Results Test).'))
            continue
        items = data if isinstance(data, list) else data.get('@graph', [data]) if isinstance(data, dict) else []
        for item in items:
            if isinstance(item, dict) and item.get('@type'):
                t = item['@type']
                page['schema_types'].extend(t if isinstance(t, list) else [t])
                for key in ('datePublished', 'dateModified', 'price'):
                    if key in item and item[key] in ('', None):
                        issues.append(_issue('warning', 'Structured data', f'{t}: empty "{key}".', f'Fill in or remove "{key}".'))
    if not p.jsonld:
        issues.append(_issue('notice', 'Structured data', 'No structured data.',
                             'Add relevant schema.org markup (e.g. BreadcrumbList, Article). It does not guarantee rich results.'))
    # Social / images / content
    if not page['og_image']:
        issues.append(_issue('notice', 'Social', 'No og:image.', 'Add a share image (1200×630) for link previews.'))
    if p.imgs_no_alt:
        issues.append(_issue('warning', 'Images', f'{p.imgs_no_alt} image(s) without an alt attribute.',
                             'Describe meaningful images with alt text; use alt="" for decorative ones.'))
    if words < THIN_WORDS:
        issues.append(_issue('notice', 'Content', f'Thin content (~{words} words of text).',
                             'Add genuinely useful detail for visitors; thin pages rarely rank.'))
    if not p.lang:
        issues.append(_issue('notice', 'Language', 'Missing <html lang>.', 'Set the page language, e.g. lang="en".'))
    return _finish(page)


def _finish(page):
    penalty = sum(SEVERITY_WEIGHT[i['severity']] for i in page['issues'])
    page['score'] = max(0, 100 - penalty)
    page['counts'] = {s: sum(1 for i in page['issues'] if i['severity'] == s) for s in SEVERITY_WEIGHT}
    return page


def site_checks(client, sitemap_status, paths):
    from .models import Redirect, SEOData, SiteSettings
    checks = []

    def add(ok, name, detail, fix=''):
        checks.append({'ok': ok, 'name': name, 'detail': detail, 'fix': fix})

    r = client.get('/robots.txt')
    robots = r.content.decode('utf-8', 'ignore') if r.status_code == 200 else ''
    add(r.status_code == 200, 'robots.txt reachable', f'HTTP {r.status_code}')
    add('sitemap:' in robots.lower(), 'robots.txt lists the sitemap',
        'Found a Sitemap: line' if 'sitemap:' in robots.lower() else 'No Sitemap: line', 'Add "Sitemap: <url>" to robots.txt.')
    blocks_all = bool(re.search(r'(?im)^disallow:\s*/\s*$', robots))
    add(not blocks_all, 'robots.txt does not block the whole site',
        'Disallow: / found — the entire site is blocked!' if blocks_all else 'No site-wide block')
    add(sitemap_status == 200 and bool(paths), 'XML sitemap', f'{len(paths)} URLs listed' if paths else f'HTTP {sitemap_status}')

    redirect_problems = []
    path_set = set(paths)
    for rd in Redirect.objects.filter(is_active=True):
        try:
            rd.clean()
        except ValidationError as e:
            msgs = '; '.join(m for v in e.message_dict.values() for m in v)
            redirect_problems.append({'id': rd.id, 'rule': f'{rd.old_path} → {rd.new_path}', 'problem': msgs})
        if rd.old_path in path_set:
            redirect_problems.append({'id': rd.id, 'rule': f'{rd.old_path} → {rd.new_path}',
                                      'problem': 'Redirected URL is still listed in the sitemap.'})
    add(not redirect_problems, 'Redirect rules',
        f'{Redirect.objects.filter(is_active=True).count()} active, {len(redirect_problems)} with problems')

    try:
        ga = (SiteSettings.get_settings().google_analytics_id or '').strip()
    except Exception:
        ga = ''
    return checks, redirect_problems, ga, SEOData.objects.order_by('path')


def run_audit():
    client, host = _client()
    started = timezone.now()
    paths, sitemap_status = sitemap_paths(client)
    pages = [audit_page(client, p) for p in paths]

    # Duplicate titles / descriptions across pages
    by_title, by_desc = defaultdict(list), defaultdict(list)
    for pg in pages:
        if pg.get('title'):
            by_title[pg['title'].lower()].append(pg['path'])
        if pg.get('description'):
            by_desc[pg['description'].lower()].append(pg['path'])
    for pg in pages:
        if pg.get('title') and len(by_title[pg['title'].lower()]) > 1:
            others = [x for x in by_title[pg['title'].lower()] if x != pg['path']]
            pg['issues'].append(_issue('warning', 'Title', f'Same title as {", ".join(others[:3])}.', 'Give every page a unique title.'))
        if pg.get('description') and len(by_desc[pg['description'].lower()]) > 1:
            others = [x for x in by_desc[pg['description'].lower()] if x != pg['path']]
            pg['issues'].append(_issue('notice', 'Meta description', f'Same description as {", ".join(others[:3])}.',
                                       'Write a unique description for each page.'))
        _finish(pg)

    checks, redirect_problems, ga, _ = site_checks(client, sitemap_status, paths)
    result = {
        'ran_at': started.isoformat(),
        'duration_s': round((timezone.now() - started).total_seconds(), 1),
        'host': host,
        'pages': sorted(pages, key=lambda x: x['score']),
        'site_checks': checks,
        'redirect_problems': redirect_problems,
        'ga_id': ga,
    }
    result['summary'] = summarize(result)
    cache.set(CACHE_KEY, result, CACHE_SECONDS)
    return result


def summarize(result):
    pages = result['pages']
    total = len(pages)
    counts = {s: sum(p['counts'][s] for p in pages) for s in SEVERITY_WEIGHT}
    avg = round(sum(p['score'] for p in pages) / total) if total else 0
    by_check = defaultdict(int)
    for p in pages:
        for i in p['issues']:
            by_check[(i['severity'], i['check'])] += 1
    top = sorted(by_check.items(), key=lambda kv: (-SEVERITY_WEIGHT[kv[0][0]], -kv[1]))[:8]
    return {
        'pages': total,
        'avg_score': avg,
        'counts': counts,
        'healthy_pages': sum(1 for p in pages if not p['counts']['critical'] and not p['counts']['warning']),
        'failed_site_checks': sum(1 for c in result['site_checks'] if not c['ok']),
        'top_issues': [{'severity': k[0], 'check': k[1], 'pages': v} for k, v in top],
    }


def cached_audit():
    return cache.get(CACHE_KEY)


def issues_csv(result):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(['URL', 'Score', 'Severity', 'Check', 'Issue', 'Recommended fix', 'Audited at (UTC)'])
    base = canonical_base()

    def safe(v):  # neutralise spreadsheet formula injection
        v = str(v)
        return "'" + v if v[:1] in ('=', '+', '-', '@') else v
    for p in result['pages']:
        if not p['issues']:
            w.writerow([base + p['path'], p['score'], '', '', 'No issues found', '', result['ran_at']])
        for i in p['issues']:
            w.writerow([base + p['path'], p['score'], i['severity'], i['check'], safe(i['message']), safe(i['fix']), result['ran_at']])
    return buf.getvalue()
