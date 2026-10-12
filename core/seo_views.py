"""Admin SEO dashboard views."""
from datetime import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import seo_audit
from .models import Redirect, SEOData


@staff_member_required(login_url='admin:login')
def admin_seo_dashboard(request):
    result = seo_audit.cached_audit()
    if result is None:
        result = seo_audit.run_audit()
    ran_at = datetime.fromisoformat(result['ran_at'])
    rendered_titles = {p['path']: p.get('title', '') for p in result['pages']}
    overrides = []
    for row in SEOData.objects.order_by('path'):
        rendered = rendered_titles.get(row.path)
        overrides.append({
            'row': row,
            'in_sitemap': row.path in rendered_titles,
            'applied': (rendered or '').strip() == (row.meta_title or '').strip() if rendered is not None else None,
            'title_len': len(row.meta_title or ''),
            'desc_len': len(row.meta_description or ''),
        })
    context = {
        'title': 'SEO Dashboard',
        'audit': result,
        'summary': result['summary'],
        'ran_at': ran_at,
        'overrides': overrides,
        'redirect_count': Redirect.objects.filter(is_active=True).count(),
        'base': seo_audit.canonical_base(),
        'thresholds': {'title': (seo_audit.TITLE_MIN, seo_audit.TITLE_MAX), 'desc': (seo_audit.DESC_MIN, seo_audit.DESC_MAX)},
    }
    return render(request, 'admin/seo_dashboard.html', context)


@staff_member_required(login_url='admin:login')
@require_POST
def admin_seo_run_audit(request):
    result = seo_audit.run_audit()
    s = result['summary']
    messages.success(request, f"Audit finished: {s['pages']} pages checked in {result['duration_s']}s — "
                              f"{s['counts']['critical']} critical, {s['counts']['warning']} warnings, {s['counts']['notice']} notices.")
    return redirect('admin_seo_dashboard')


@staff_member_required(login_url='admin:login')
def admin_seo_export(request):
    result = seo_audit.cached_audit() or seo_audit.run_audit()
    resp = HttpResponse(seo_audit.issues_csv(result), content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="projectshub_seo_audit_{datetime.now():%Y-%m-%d_%H-%M}.csv"'
    return resp
