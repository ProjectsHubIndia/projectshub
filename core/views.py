import os
import shutil
from datetime import datetime
import json
import logging
import random
import html
import re
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.db import models
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.core import signing
from django.core.cache import cache
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test

superuser_required = user_passes_test(lambda u: u.is_active and u.is_superuser, login_url='admin:login')

from .models import (
    SiteSettings, NavigationItem, StatItem,
    ProjectCategory, Technology, Project,
    ToolCategory, AITool,
    Service,
    CaseStudy,
    Testimonial, FAQ,
    BlogCategory, BlogPost,
    ContactInquiry, ContactMessage, ProjectGateLead,
    IdeaSubmission, WorkshopCard, WorkshopDay, WorkshopEnrollment,
    PricingPlan,
    SEOData, Redirect,
    ChatbotConversation, ChatbotMessage,
    AdminGuideNote
)
from .seo import get_base_url

logger = logging.getLogger(__name__)


def error_404(request, exception=None):
    if request.path.startswith('/admin/') or request.path.startswith('/admin-404'):
        return render(request, 'admin/404.html', status=404)
    return render(request, 'core/error404.html', status=404)


def error_500(request):
    return render(request, 'core/error500.html', status=500)


def health_check(request):
    """Production health check probe for orchestrators and monitoring."""
    from django.db import connection
    db_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        db_ok = False

    status_code = 200 if db_ok else 503
    return JsonResponse({
        'status': 'healthy' if db_ok else 'unhealthy',
        'database': 'connected' if db_ok else 'disconnected',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }, status=status_code)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ── Pages ──────────────────────────────────────────────────────────────────────

@ensure_csrf_cookie
def index(request):
    """Homepage — passes dynamic, database-backed content to the template."""
    # Projects for showcase
    featured_qs = Project.objects.filter(is_active=True, show_on_index=True).order_by('order', '-created_at')
    if not featured_qs.exists():
        featured_qs = Project.objects.filter(is_active=True).order_by('order', '-created_at')[:6]

    project_categories = ProjectCategory.objects.all().order_by('order')
    technologies = Technology.objects.all().order_by('order')

    # Tools, Case studies, Testimonials, FAQs
    free_tools = AITool.objects.filter(is_published=True).order_by('sort_order')[:9]
    case_studies = CaseStudy.objects.filter(is_published=True).prefetch_related('metrics').order_by('sort_order')[:6]
    testimonials = Testimonial.objects.filter(is_published=True).order_by('sort_order')
    faqs = FAQ.objects.filter(is_published=True).order_by('sort_order')

    # Stats
    stat_items_numbers = StatItem.objects.filter(section='numbers', is_active=True).order_by('order')
    stat_items_about = StatItem.objects.filter(section='about', is_active=True).order_by('order')

    # Services split
    services_student = Service.objects.filter(
        is_published=True, target_audience__in=['student', 'both']
    ).prefetch_related('features').order_by('sort_order')
    services_business = Service.objects.filter(
        is_published=True, target_audience__in=['business', 'both']
    ).prefetch_related('features').order_by('sort_order')

    pricing_plans = PricingPlan.objects.filter(is_active=True).prefetch_related('features')

    context = {
        'index_projects': featured_qs,
        'project_categories': project_categories,
        'technologies': technologies,
        'free_tools': free_tools,
        'case_studies': case_studies,
        'testimonials': testimonials,
        'faqs': faqs,
        'stat_items_numbers': stat_items_numbers,
        'stat_items_about': stat_items_about,
        'services_student': services_student,
        'services_business': services_business,
        'pricing_plans': pricing_plans,
    }
    return render(request, 'core/index.html', context)


def projects_page(request):
    """Filterable projects directory with AJAX/HTMX support."""
    qs = Project.objects.filter(is_active=True).prefetch_related('technologies', 'category_ref').order_by('order', '-created_at')

    category_slug = request.GET.get('category', '').strip()
    tech_slug = request.GET.get('tech', '').strip()
    query = request.GET.get('q', '').strip()

    if category_slug and category_slug != 'all':
        qs = qs.filter(Q(category=category_slug) | Q(category_ref__slug=category_slug))

    if tech_slug and tech_slug != 'all':
        qs = qs.filter(Q(technologies__slug=tech_slug) | Q(tags__icontains=tech_slug)).distinct()

    if query:
        qs = qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        ).distinct()

    is_ajax = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return render(request, 'core/partials/project_cards_grid.html', {'projects': qs})

    categories = ProjectCategory.objects.all().order_by('order')
    technologies = Technology.objects.all().order_by('order')

    context = {
        'projects': qs,
        'categories': categories,
        'technologies': technologies,
        'active_category': category_slug or 'all',
        'active_tech': tech_slug or 'all',
        'search_query': query,
    }
    return render(request, 'core/projects.html', context)


def project_detail(request, project_id=None, slug=None):
    """Project detail page — lookup by id or slug."""
    if slug:
        project = get_object_or_404(
            Project.objects.prefetch_related(
                'detail_images', 'highlights', 'diagrams',
                'timeline_phases', 'price_features', 'technologies'
            ),
            slug=slug, is_active=True
        )
    else:
        project = get_object_or_404(
            Project.objects.prefetch_related(
                'detail_images', 'highlights', 'diagrams',
                'timeline_phases', 'price_features', 'technologies'
            ),
            id=project_id, is_active=True
        )

    related_projects = (
        Project.objects
        .filter(is_active=True, category=project.category)
        .exclude(id=project.id)
        .order_by('order', '-created_at')[:3]
    )
    context = {
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'core/project_detail.html', context)


def tools_page(request):
    """Free AI tools portal."""
    categories = ToolCategory.objects.annotate(
        tool_count=Count('tools', filter=Q(tools__is_published=True))
    ).order_by('order')
    tools = AITool.objects.filter(is_published=True).select_related('category').order_by('sort_order', 'name')
    featured_tools = [t for t in tools if t.featured]
    context = {
        'categories': categories,
        'tools': tools,
        'featured_tools': featured_tools,
        'total_count': len(tools),
    }
    return render(request, 'core/tools.html', context)


def case_studies_page(request):
    """Case studies and client success stories."""
    case_studies = CaseStudy.objects.filter(is_published=True).prefetch_related('metrics').order_by('sort_order', '-created_at')
    context = {
        'case_studies': case_studies,
    }
    return render(request, 'core/case_studies.html', context)


def ai_roadmap(request):
    return render(request, 'core/AI_roadmap.html')


def ai_development(request):
    service = Service.objects.filter(slug='ai-development').prefetch_related('features').first()
    return render(request, 'core/ai_development.html', {'service': service})


def ai_automation(request):
    service = Service.objects.filter(slug='ai-automation').prefetch_related('features').first()
    return render(request, 'core/ai_automation.html', {'service': service})


def ai_integration(request):
    service = Service.objects.filter(slug='ai-integration').prefetch_related('features').first()
    return render(request, 'core/ai_integration.html', {'service': service})


def industries(request):
    return render(request, 'core/industries.html')


def workshop_page(request):
    workshops = WorkshopCard.objects.filter(is_active=True).prefetch_related('days').order_by('order', '-created_at')
    featured = next((w for w in workshops if w.is_featured), None) or next(iter(workshops), None)
    context = {
        'workshops': workshops,
        'workshop': featured,
    }
    return render(request, 'core/workshop.html', context)


def workshop_detail(request, workshop_id):
    workshop = get_object_or_404(
        WorkshopCard.objects.prefetch_related('days'),
        id=workshop_id, is_active=True
    )
    other_workshops = (
        WorkshopCard.objects
        .filter(is_active=True)
        .exclude(id=workshop_id)
        .order_by('order', '-created_at')[:3]
    )
    context = {
        'workshop': workshop,
        'other_workshops': other_workshops,
    }
    return render(request, 'core/workshop_detail.html', context)


def workshop_day_detail(request, workshop_id, day_number):
    workshop = get_object_or_404(WorkshopCard, id=workshop_id, is_active=True)
    day = get_object_or_404(WorkshopDay, workshop=workshop, day_number=day_number)
    days = list(workshop.days.order_by('day_number'))
    prev_day = next((d for d in reversed(days) if d.day_number < day_number), None)
    next_day = next((d for d in days if d.day_number > day_number), None)
    context = {
        'workshop': workshop,
        'day': day,
        'prev_day': prev_day,
        'next_day': next_day,
        'total_days': len(days),
    }
    return render(request, 'core/workshop-day.html', context)


def blog_page(request):
    posts = BlogPost.objects.filter(is_active=True, is_published=True).order_by(
        '-is_featured', 'order', '-published_at', '-created_at'
    )
    return render(request, 'core/blog.html', {'posts': posts})


def blog_detail(request, slug):
    post = get_object_or_404(
        BlogPost.objects.prefetch_related('sections'),
        slug=slug, is_active=True
    )
    related_posts = (
        BlogPost.objects
        .filter(is_active=True, category=post.category)
        .exclude(pk=post.pk)[:3]
    )
    return render(request, 'core/blog_detail.html', {
        'post': post,
        'related_posts': related_posts,
    })


def terms(request):
    return render(request, 'core/terms.html')


def refund(request):
    return render(request, 'core/refund.html')


def privacy(request):
    return render(request, 'core/privacy.html')


def html_sitemap(request):
    return render(request, 'core/sitemap.html')


# ── Form Endpoints ─────────────────────────────────────────────────────────────

def _parse_request_data(request):
    """Parse JSON or form-encoded POST data."""
    if request.content_type and 'application/json' in request.content_type:
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return {}
    return request.POST


# ── Catch Code (Captcha) Generator ───────────────────────────────────────────

def generate_captcha_svg(code):
    """Generate a clean, high-DPI vector SVG for Catch Code (Captcha) verification."""
    width = 140
    height = 46
    colors = ['#1e293b', '#2563eb', '#7c3aed', '#059669', '#d97706', '#dc2626', '#0284c7']
    
    # Noise background lines
    lines_svg = []
    for _ in range(3):
        x1 = random.randint(0, 30)
        y1 = random.randint(6, height - 6)
        x2 = random.randint(width - 30, width)
        y2 = random.randint(6, height - 6)
        stroke = random.choice(['rgba(99, 102, 241, 0.35)', 'rgba(59, 130, 246, 0.3)', 'rgba(16, 185, 129, 0.3)'])
        lines_svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{random.choice([1.5, 2])}" />')
    
    # Noise dots
    dots_svg = []
    for _ in range(16):
        cx = random.randint(6, width - 6)
        cy = random.randint(6, height - 6)
        r = random.uniform(1.2, 2.2)
        dots_svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="rgba(100, 116, 139, 0.22)" />')
        
    # Letters with tilt, color, and positioning
    char_count = len(code)
    spacing = width / (char_count + 1)
    chars_svg = []
    for i, ch in enumerate(code):
        x = int(spacing * (i + 0.8))
        y = random.randint(29, 34)
        angle = random.randint(-18, 18)
        color = random.choice(colors)
        font_size = random.randint(22, 25)
        chars_svg.append(
            f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial, Helvetica, sans-serif" '
            f'font-size="{font_size}" font-weight="900" transform="rotate({angle} {x} {y})">{html.escape(ch)}</text>'
        )
        
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" fill="#f1f5f9" rx="10" />'
        f'{"".join(lines_svg)}'
        f'{"".join(dots_svg)}'
        f'{"".join(chars_svg)}'
        f'</svg>'
    )


def api_captcha(request):
    """API endpoint to generate a new Catch Code (Captcha) for the contact form."""
    chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    code = ''.join(random.choices(chars, k=5))
    
    # Save in session
    request.session['contact_captcha'] = code.upper()
    request.session.modified = True
    
    # Signed token fallback (stateless / cross-tab / cache resilience)
    token = signing.dumps(code.upper(), salt='captcha-salt')
    svg = generate_captcha_svg(code)
    
    return JsonResponse({
        'success': True,
        'token': token,
        'svg': svg,
    })


def contact_page(request):
    """Separate dedicated Contact Us page with full SEO and inquiry handling."""
    if request.method == 'POST':
        return contact_submit(request)

    contact_faqs = FAQ.objects.filter(is_published=True).order_by('sort_order')[:6]
    context = {
        'contact_faqs': contact_faqs,
    }
    return render(request, 'core/contact.html', context)


@require_POST
def contact_submit(request):
    """Handle contact form submission with lead recording & email notification."""
    try:
        data = _parse_request_data(request)
        name = (data.get('full_name') or data.get('name') or '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        subject = data.get('subject', '').strip() or 'Project Inquiry'
        message = data.get('message', '').strip()
        source_page = data.get('source_page', '/#contact')

        errors = {}
        if not name:
            errors['name'] = 'Full name is required.'
        if not email:
            errors['email'] = 'Valid email is required.'
        if not message:
            errors['message'] = 'Message is required.'

        # Honeypot spam bot trap (silently drop bot submissions)
        if data.get('hp_company_url'):
            return JsonResponse({'success': True, 'message': 'Thank you! Your message has been received.'})

        # Catch Code (Captcha) verification
        catch_code = (data.get('catch_code') or data.get('captcha') or '').strip().upper()
        captcha_token = (data.get('captcha_token') or '').strip()
        session_captcha = request.session.get('contact_captcha', '').upper()

        token_captcha = None
        if captcha_token:
            cache_key = f"used_captcha:{captcha_token}"
            if cache.get(cache_key):
                errors['catch_code'] = 'This verification code has already been used. Please refresh the code.'
            else:
                try:
                    token_captcha = signing.loads(captcha_token, salt='captcha-salt', max_age=600)
                except Exception:
                    token_captcha = None

        if 'catch_code' not in errors:
            if not catch_code:
                errors['catch_code'] = 'Catch code (security verification) is required.'
            elif catch_code != session_captcha and catch_code != token_captcha:
                errors['catch_code'] = 'Invalid catch code. Please enter the characters shown in the image.'

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # Clear used session captcha and mark token as spent
        if 'contact_captcha' in request.session:
            del request.session['contact_captcha']
            request.session.modified = True
        if captcha_token:
            cache.set(f"used_captcha:{captcha_token}", True, 600)

        ip_addr = get_client_ip(request)

        # 1. Record in ContactInquiry
        inquiry = ContactInquiry.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            source_page=source_page,
            status='new',
            ip_address=ip_addr,
        )

        # 2. Record in legacy ContactMessage
        ContactMessage.objects.create(
            full_name=name,
            email=email,
            subject=subject,
            message=message,
            ip_address=ip_addr,
        )

        # 3. Attempt email notification (graceful failure)
        try:
            send_mail(
                subject=f"[ProjectsHub Lead] {subject} from {name}",
                message=f"Name: {name}\nEmail: {email}\nPhone: {phone}\nSubject: {subject}\nSource: {source_page}\n\nMessage:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'support@projectshub.co.in',
                recipient_list=['support@projectshub.co.in'],
                fail_silently=True,
            )
        except Exception as mail_err:
            logger.warning(f"Email sending failed: {mail_err}")

        return JsonResponse({
            'success': True,
            'message': "Thank you! Your message has been received. We will get back to you within 24 hours."
        })
    except Exception as e:
        logger.error(f"Contact submit error: {e}")
        return JsonResponse(
            {'success': False, 'message': 'An unexpected error occurred. Please try again or email us directly.'},
            status=500
        )


@require_POST
def gate_submit(request):
    try:
        data = _parse_request_data(request)
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        college_or_org = data.get('college_or_org', '').strip()

        errors = {}
        if not full_name:
            errors['full_name'] = 'Full name is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not college_or_org:
            errors['college_or_org'] = 'College / Organization is required.'

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        ProjectGateLead.objects.get_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'college_or_org': college_or_org,
                'ip_address': get_client_ip(request),
            }
        )
        return JsonResponse({'success': True})
    except Exception:
        return JsonResponse({'success': False, 'message': 'Something went wrong.'}, status=500)


@require_POST
def idea_submit(request):
    try:
        data = _parse_request_data(request)
        full_name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        project_title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        budget = data.get('budget', '').strip()
        timeline = data.get('timeline', '').strip()
        agreed = bool(data.get('agreed', False))

        errors = {}
        if not full_name:
            errors['name'] = 'Full name is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not project_title:
            errors['title'] = 'Project title is required.'
        if not description:
            errors['description'] = 'Project description is required.'

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        IdeaSubmission.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            project_title=project_title,
            description=description,
            budget=budget,
            timeline=timeline,
            agreed_to_terms=agreed,
            ip_address=get_client_ip(request),
        )
        return JsonResponse({
            'success': True,
            'message': "Your idea has been submitted! We'll be in touch soon."
        })
    except Exception:
        return JsonResponse({'success': False, 'message': 'Something went wrong. Please try again.'}, status=500)


@require_POST
def enroll_submit(request):
    try:
        data = _parse_request_data(request)
        full_name = data.get('fullName', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        experience = data.get('experience', '').strip()
        referral = data.get('referral', '').strip()
        message = data.get('message', '').strip()
        agreed = bool(data.get('agreed', False))
        workshop_id = data.get('workshopId')

        errors = {}
        if not full_name:
            errors['fullName'] = 'Full name is required.'
        if not email:
            errors['email'] = 'Email is required.'

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        workshop = None
        if workshop_id:
            try:
                workshop = WorkshopCard.objects.get(id=workshop_id, is_active=True)
            except WorkshopCard.DoesNotExist:
                pass

        if workshop and WorkshopEnrollment.objects.filter(workshop=workshop, email=email).exists():
            return JsonResponse({'success': True, 'message': "You're already enrolled in this workshop!"})

        WorkshopEnrollment.objects.create(
            workshop=workshop,
            full_name=full_name,
            email=email,
            phone=phone,
            experience=experience,
            referral=referral,
            message=message,
            agreed_to_terms=agreed,
            ip_address=get_client_ip(request),
        )
        return JsonResponse({'success': True, 'message': 'Enrollment received! Check your email for workshop details.'})
    except Exception:
        return JsonResponse({'success': False, 'message': 'Something went wrong. Please try again.'}, status=500)


# ── JSON APIs ──────────────────────────────────────────────────────────────────

def api_projects(request):
    qs = Project.objects.filter(is_active=True).prefetch_related('technologies', 'category_ref')
    if request.GET.get('index_only'):
        qs = qs.filter(show_on_index=True)
    data = [
        {
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'description': p.description,
            'image': p.get_image_src(),
            'tags': p.get_tags_list(),
            'category': p.category,
            'detail_url': f'/projects/{p.slug}/' if p.slug else f'/projects/{p.id}/',
        }
        for p in qs
    ]
    return JsonResponse({'projects': data})


def api_pricing(request):
    plans = PricingPlan.objects.filter(is_active=True).prefetch_related('features')
    data = [
        {
            'id': plan.id,
            'name': plan.name,
            'icon_type': plan.icon_type,
            'description': plan.description,
            'is_free': plan.is_free,
            'monthly_price': str(plan.monthly_price),
            'yearly_price': str(plan.yearly_price),
            'features': [f.feature for f in plan.features.all()],
        }
        for plan in plans
    ]
    return JsonResponse({'plans': data})


def api_workshops(request):
    workshops = WorkshopCard.objects.filter(is_active=True).prefetch_related('days')
    data = [
        {
            'id': w.id,
            'title': w.title,
            'subtitle': w.subtitle,
            'date': w.date,
            'price_label': w.price_label,
            'days': [{'day_number': d.day_number, 'title': d.title, 'outcome': d.outcome} for d in w.days.all()]
        }
        for w in workshops
    ]
    return JsonResponse({'workshops': data})


def api_blog(request):
    posts = BlogPost.objects.filter(is_active=True)
    data = [
        {
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'excerpt': p.excerpt,
            'author': p.author_name,
            'detail_url': f'/blog/{p.slug}/',
        }
        for p in posts
    ]
    return JsonResponse({'posts': data})


# ── SEO Endpoints ─────────────────────────────────────────────────────────────

def robots_txt(request):
    base_url = get_base_url(request)
    lines = [
        'User-agent: *',
        'Allow: /',
        '',
        'Disallow: /admin/',
        'Disallow: /contact/submit/',
        'Disallow: /gate/',
        'Disallow: /idea/',
        'Disallow: /enroll/',
        'Disallow: /api/',
        '',
        f'Sitemap: {base_url}/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def sitemap_xml(request):
    base_url = get_base_url(request)
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    static_pages = [
        ('/', '1.0', 'daily'),
        ('/projects/', '0.9', 'weekly'),
        ('/tools/', '0.9', 'weekly'),
        ('/case-studies/', '0.8', 'monthly'),
        ('/workshop/', '0.8', 'weekly'),
        ('/ai-roadmap/', '0.8', 'monthly'),
        ('/services/ai-development/', '0.8', 'monthly'),
        ('/services/ai-automation/', '0.8', 'monthly'),
        ('/services/ai-integration/', '0.8', 'monthly'),
        ('/industries/', '0.8', 'monthly'),
        ('/blog/', '0.8', 'weekly'),
        ('/contact/', '0.8', 'monthly'),
        ('/privacy/', '0.3', 'yearly'),
        ('/terms/', '0.3', 'yearly'),
        ('/refund/', '0.3', 'yearly'),
        ('/sitemap/', '0.3', 'monthly'),
    ]

    for path, priority, freq in static_pages:
        xml.append('  <url>')
        xml.append(f'    <loc>{base_url}{path}</loc>')
        xml.append(f'    <changefreq>{freq}</changefreq>')
        xml.append(f'    <priority>{priority}</priority>')
        xml.append('  </url>')

    for p in Project.objects.filter(is_active=True).order_by('-created_at'):
        loc = f"{base_url}/projects/{p.slug}/" if p.slug else f"{base_url}/projects/{p.id}/"
        xml.append('  <url>')
        xml.append(f'    <loc>{loc}</loc>')
        xml.append('    <changefreq>monthly</changefreq>')
        xml.append('    <priority>0.7</priority>')
        xml.append('  </url>')

    for b in BlogPost.objects.filter(is_active=True).order_by('-published_at'):
        xml.append('  <url>')
        xml.append(f'    <loc>{base_url}/blog/{b.slug}/</loc>')
        if b.published_at:
            xml.append(f'    <lastmod>{b.published_at.strftime("%Y-%m-%d")}</lastmod>')
        xml.append('    <changefreq>monthly</changefreq>')
        xml.append('    <priority>0.7</priority>')
        xml.append('  </url>')

    xml.append('</urlset>')
    return HttpResponse('\n'.join(xml), content_type='application/xml')


# ═══════════════════════════════════════════════════════════════════════════════
# AI CHATBOT DATA & TELEMETRY API
# ═══════════════════════════════════════════════════════════════════════════════

@csrf_exempt
@require_POST
def api_chatbot_message(request):
    """
    Ingests messages from the frontend AI Chatbot widget.
    Saves conversation telemetry, visitor context, messages, and detects leads in real-time.
    """
    try:
        data = _parse_request_data(request)
        session_id = data.get('session_id', '').strip()
        if not session_id:
            return JsonResponse({'success': False, 'error': 'session_id is required'}, status=400)

        sender = data.get('sender', 'user').strip().lower()
        if sender not in ('user', 'bot', 'agent'):
            sender = 'user'

        message_text = data.get('message', '').strip()
        if not message_text:
            return JsonResponse({'success': False, 'error': 'message cannot be empty'}, status=400)

        # Rate limit: Max 30 messages per minute per IP
        ip_addr = get_client_ip(request)
        rate_key = f"chat_rate:{ip_addr}"
        msg_count = cache.get(rate_key, 0)
        if msg_count >= 30:
            return JsonResponse({'success': False, 'error': 'Rate limit exceeded. Please wait a minute.'}, status=429)
        cache.set(rate_key, msg_count + 1, 60)

        # Message length validation
        if len(message_text) > 1000:
            return JsonResponse({'success': False, 'error': 'Message exceeds maximum allowed length of 1000 characters.'}, status=400)

        page_url = data.get('page_url', '').strip() or request.META.get('HTTP_REFERER', '/')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Get or create conversation
        conv, created = ChatbotConversation.objects.get_or_create(
            session_id=session_id,
            defaults={
                'page_url': page_url,
                'ip_address': ip_addr,
                'user_agent': user_agent,
                'status': 'active',
            }
        )

        # Update metadata if blank
        if not conv.ip_address and ip_addr:
            conv.ip_address = ip_addr
        if page_url and conv.page_url != page_url:
            conv.page_url = page_url

        # Check for user info in payload
        user_name = data.get('user_name', '').strip()
        user_email = data.get('user_email', '').strip()
        user_phone = data.get('user_phone', '').strip()
        if user_name and not conv.user_name:
            conv.user_name = user_name
        if user_email and not conv.user_email:
            conv.user_email = user_email
            conv.status = 'lead'
        if user_phone and not conv.user_phone:
            conv.user_phone = user_phone
            conv.status = 'lead'

        # Lead intelligence: detect email or phone in message
        if sender == 'user':
            email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', message_text)
            if email_match and not conv.user_email:
                conv.user_email = email_match.group(0)
                conv.status = 'lead'

            phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', message_text)
            if phone_match and not conv.user_phone:
                conv.user_phone = phone_match.group(0).strip()
                conv.status = 'lead'

            # Detect service interest keywords
            lower_msg = message_text.lower()
            if any(k in lower_msg for k in ['workshop', 'bootcamp', 'course']):
                conv.service_interest = '3-Day AI Bootcamp / Workshops'
            elif any(k in lower_msg for k in ['mentorship', '1-on-1', 'career']):
                conv.service_interest = '1-on-1 AI Mentorship'
            elif any(k in lower_msg for k in ['hire', 'build', 'custom', 'mvp', 'business']):
                conv.service_interest = 'Custom AI Development'
            elif any(k in lower_msg for k in ['project', 'code', 'buy', 'pricing']):
                conv.service_interest = 'Projects & Source Code'

        conv.save()

        msg = ChatbotMessage.objects.create(
            conversation=conv,
            sender=sender,
            message=message_text,
        )

        return JsonResponse({
            'success': True,
            'conversation_id': conv.id,
            'message_id': msg.id,
            'status': conv.status,
            'is_lead': conv.status == 'lead',
        })
    except Exception as e:
        logger.exception("Error saving chatbot message")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def api_chatbot_history(request):
    """Returns past message history for a given session token."""
    session_id = request.GET.get('session_id', '').strip()
    if not session_id:
        return JsonResponse({'messages': []})

    conv = ChatbotConversation.objects.filter(session_id=session_id).first()
    if not conv:
        return JsonResponse({'messages': []})

    msgs = [
        {
            'id': m.id,
            'sender': m.sender,
            'text': m.message,
            'timestamp': m.timestamp.isoformat(),
            'isUser': m.sender == 'user',
        }
        for m in conv.messages.all().order_by('timestamp')
    ]
    return JsonResponse({'messages': msgs, 'status': conv.status})


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN MASTER GUIDE & OPERATIONS MANUAL
# ═══════════════════════════════════════════════════════════════════════════════

@staff_member_required(login_url='admin:login')
def admin_guide_view(request):
    """
    Renders the Master Admin Guide and Operations Manual with live status metrics,
    categorized instructions, direct 1-click action shortcuts, and custom admin notes.
    """
    notes = AdminGuideNote.objects.all().order_by('-is_pinned', 'order', '-created_at')

    # Live platform metrics for guide cards
    stats = {
        'total_projects': Project.objects.count(),
        'active_projects': Project.objects.filter(is_active=True).count(),
        'featured_projects': Project.objects.filter(is_active=True, show_on_index=True).count(),
        'project_categories': ProjectCategory.objects.count(),
        'total_tools': AITool.objects.count(),
        'published_tools': AITool.objects.filter(is_published=True).count(),
        'featured_tools': AITool.objects.filter(featured=True).count(),
        'tool_categories': ToolCategory.objects.count(),
        'total_case_studies': CaseStudy.objects.count(),
        'published_case_studies': CaseStudy.objects.filter(is_published=True).count(),
        'total_services': Service.objects.count(),
        'total_workshops': WorkshopCard.objects.count(),
        'workshop_days': WorkshopDay.objects.count(),
        'total_enrollments': WorkshopEnrollment.objects.count(),
        'pending_enrollments': WorkshopEnrollment.objects.filter(status='pending').count(),
        'total_blogs': BlogPost.objects.count(),
        'published_blogs': BlogPost.objects.filter(is_published=True).count(),
        'blog_categories': BlogCategory.objects.count(),
        'total_inquiries': ContactInquiry.objects.count(),
        'new_inquiries': ContactInquiry.objects.filter(status='new').count(),
        'total_ideas': IdeaSubmission.objects.count(),
        'new_ideas': IdeaSubmission.objects.filter(status='new').count(),
        'chatbot_conversations': ChatbotConversation.objects.count(),
        'chatbot_leads': ChatbotConversation.objects.filter(status='lead').count(),
        'gate_leads': ProjectGateLead.objects.count(),
        'nav_items': NavigationItem.objects.count(),
        'seo_items': SEOData.objects.count(),
        'redirects': Redirect.objects.count(),
        'site_settings': SiteSettings.get_settings(),
    }

    context = {
        **admin.site.each_context(request),
        'title': 'Project Guide & Master Operations Manual',
        'guide_notes': notes,
        'guide_stats': stats,
        'has_permission': True,
    }
    return render(request, 'admin/guide.html', context)


@staff_member_required(login_url='admin:login')
@require_POST
def toggle_guide_note(request, note_id):
    """AJAX endpoint to quickly toggle completion status of an admin guide checklist note."""
    note = get_object_or_404(AdminGuideNote, pk=note_id)
    note.is_completed = not note.is_completed
    note.save(update_fields=['is_completed', 'updated_at'])
    return JsonResponse({
        'status': 'ok',
        'note_id': note.id,
        'is_completed': note.is_completed,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# MEDIA & ASSETS STORAGE MANAGER (ADMIN VIEW & DELETION CONTROLLER)
# ═══════════════════════════════════════════════════════════════════════════════

def scan_all_assets():
    """
    Scans media/ and content directories in static/ (static/image/, static/video/).
    Maps each asset against:
      1. Django database model FileFields & ImageFields
      2. Template files (templates/**/*.html)
      3. CSS stylesheets (static/css/**/*.css)
      4. Scripts (static/js/**/*.js)
      5. Static config / manifests (webmanifest, json, xml)
    Returns:
      assets: list of asset dicts with size_mb, status (USED/UNUSED), used_in list, etc.
      stats: summary counts and MB totals
      folders: list of folder summary dicts
    """
    from django.apps import apps
    base_dir = str(settings.BASE_DIR)
    media_root = str(settings.MEDIA_ROOT)
    static_dir = str(settings.STATICFILES_DIRS[0])

    # 1. Collect all DB file references
    db_files = {}
    for model in apps.get_models():
        file_fields = [f.name for f in model._meta.get_fields() if isinstance(f, models.FileField)]
        if file_fields:
            try:
                for obj in model.objects.all():
                    for f in file_fields:
                        val = getattr(obj, f)
                        if val and hasattr(val, 'name') and val.name:
                            p = str(val.name).replace('\\', '/').strip()
                            obj_label = str(obj)
                            if len(obj_label) > 35:
                                obj_label = obj_label[:32] + '...'
                            db_files.setdefault(p, []).append(f"{model._meta.verbose_name.title()}: \"{obj_label}\" ({f})")
            except Exception as e:
                logger.warning(f"Error scanning model {model.__name__} file fields: {e}")

    # 2. Collect code content for string matching
    code_content = ''
    for d in ['templates', 'static/css', 'static/js', 'core']:
        full_d = os.path.join(base_dir, d)
        if os.path.exists(full_d):
            for root, dirs, files in os.walk(full_d):
                for f in files:
                    if f.endswith(('.html', '.css', '.js', '.py', '.webmanifest', '.json', '.xml', '.txt')):
                        try:
                            with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as fp:
                                code_content += fp.read() + '\n'
                        except Exception:
                            pass

    # 3. Directories to scan
    scan_roots = [
        ('media', media_root, '/media/'),
        ('static/image', os.path.join(static_dir, 'image'), '/static/image/'),
        ('static/video', os.path.join(static_dir, 'video'), '/static/video/'),
    ]

    assets = []
    folder_stats = {}
    total_bytes = 0
    used_bytes = 0
    unused_bytes = 0
    asset_id = 1

    # Protected path keywords that cannot be deleted
    protected_prefixes = [
        'static/image/logo',
        'static/image/Favicon-new',
        'static/image/favicon_io',
    ]

    for label, root_dir, url_prefix in scan_roots:
        if not os.path.exists(root_dir):
            continue

        for root, dirs, files in os.walk(root_dir):
            rel_folder = os.path.relpath(root, base_dir).replace('\\', '/')
            folder_stats.setdefault(rel_folder, {
                'path': rel_folder,
                'name': os.path.basename(rel_folder),
                'file_count': 0,
                'used_count': 0,
                'unused_count': 0,
                'total_bytes': 0,
                'total_mb': 0.0,
            })

            for f in files:
                full_path = os.path.join(root, f)
                try:
                    sz = os.path.getsize(full_path)
                    mtime = os.path.getmtime(full_path)
                except OSError:
                    continue

                rel_from_base = os.path.relpath(full_path, base_dir).replace('\\', '/')
                rel_from_root = os.path.relpath(full_path, root_dir).replace('\\', '/')
                ext = f.split('.')[-1].lower() if '.' in f else ''

                # URL computation
                url = url_prefix + rel_from_root.replace('\\', '/')

                # Size in MB
                sz_mb = round(sz / (1024 * 1024), 2)
                if sz_mb >= 0.01:
                    size_str = f"{sz_mb:.2f} MB"
                else:
                    kb = round(sz / 1024, 1)
                    size_str = f"{kb} KB"

                # Type classification
                is_image = ext in ['webp', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'avif', 'ico']
                is_video = ext in ['mp4', 'webm', 'mov', 'avi']
                is_doc = ext in ['pdf', 'zip', 'doc', 'docx', 'csv', 'txt']
                file_type = 'image' if is_image else ('video' if is_video else ('document' if is_doc else 'other'))

                # Protected status
                is_protected = any(rel_from_base.startswith(p) for p in protected_prefixes)

                # Usage Detection
                is_used = False
                used_in = []

                # A. Check DB references
                # For media files, DB usually stores relative to MEDIA_ROOT: e.g. "projects/wallpaper.webp"
                rel_media = os.path.relpath(full_path, media_root).replace('\\', '/') if full_path.startswith(media_root) else ''
                if rel_media and rel_media in db_files:
                    is_used = True
                    used_in.extend(db_files[rel_media])
                elif rel_from_root in db_files:
                    is_used = True
                    used_in.extend(db_files[rel_from_root])

                # B. Check Code references
                # Filename search or path search in templates & static files
                if f in code_content or rel_from_base in code_content or (rel_media and rel_media in code_content):
                    is_used = True
                    if not used_in:
                        used_in.append("Referenced in templates / stylesheets / manifests")

                # Count totals
                total_bytes += sz
                if is_used:
                    used_bytes += sz
                    folder_stats[rel_folder]['used_count'] += 1
                else:
                    unused_bytes += sz
                    folder_stats[rel_folder]['unused_count'] += 1

                folder_stats[rel_folder]['file_count'] += 1
                folder_stats[rel_folder]['total_bytes'] += sz

                assets.append({
                    'id': asset_id,
                    'name': f,
                    'rel_path': rel_from_base,
                    'folder': rel_folder,
                    'size_bytes': sz,
                    'size_mb': sz_mb,
                    'size_str': size_str,
                    'ext': ext,
                    'type': file_type,
                    'is_image': is_image,
                    'is_video': is_video,
                    'url': url,
                    'modified_at': datetime.fromtimestamp(mtime).strftime('%b %d, %Y, %H:%M'),
                    'is_protected': is_protected,
                    'is_used': is_used,
                    'used_in': used_in,
                    'can_delete': not is_protected,
                })
                asset_id += 1

    # Finalize folder stats
    folders = []
    for path, data in sorted(folder_stats.items()):
        data['total_mb'] = round(data['total_bytes'] / (1024 * 1024), 2)
        # Can delete folder if it has no used files and is not a top-level root
        is_top_root = path in ['media', 'static/image', 'static/video']
        data['can_delete'] = (data['used_count'] == 0) and not is_top_root
        folders.append(data)

    stats = {
        'total_assets': len(assets),
        'total_bytes': total_bytes,
        'total_mb': round(total_bytes / (1024 * 1024), 2),
        'used_count': sum(1 for a in assets if a['is_used']),
        'used_bytes': used_bytes,
        'used_mb': round(used_bytes / (1024 * 1024), 2),
        'unused_count': sum(1 for a in assets if not a['is_used']),
        'unused_bytes': unused_bytes,
        'unused_mb': round(unused_bytes / (1024 * 1024), 2),
        'total_folders': len(folders),
    }

    return assets, stats, folders


@staff_member_required(login_url='admin:login')
def admin_assets_view(request):
    """
    Renders the Media & Storage Assets Manager dashboard.
    Displays all files with size in MB, identifies used vs unused assets,
    and provides controls to safely delete unused files and folders.
    """
    assets, stats, folders = scan_all_assets()

    active_tab = request.GET.get('tab', 'assets').lower()
    filter_tab = request.GET.get('filter', 'all').lower()
    folder_filter = request.GET.get('folder', '').strip()
    type_filter = request.GET.get('type', '').strip().lower()
    search_query = request.GET.get('q', '').strip().lower()
    sort_by = request.GET.get('sort', 'size_desc').lower()

    filtered = assets

    # Filter tab: all, unused, used
    if filter_tab == 'unused':
        filtered = [a for a in filtered if not a['is_used']]
    elif filter_tab == 'used':
        filtered = [a for a in filtered if a['is_used']]

    # Folder filter
    if folder_filter:
        filtered = [a for a in filtered if a['folder'] == folder_filter]

    # Type filter
    if type_filter:
        filtered = [a for a in filtered if a['type'] == type_filter]

    # Search query
    if search_query:
        filtered = [a for a in filtered if search_query in a['name'].lower() or search_query in a['rel_path'].lower()]

    # Sorting
    if sort_by == 'size_desc':
        filtered.sort(key=lambda a: a['size_bytes'], reverse=True)
    elif sort_by == 'size_asc':
        filtered.sort(key=lambda a: a['size_bytes'])
    elif sort_by == 'name':
        filtered.sort(key=lambda a: a['name'].lower())
    elif sort_by == 'date':
        filtered.sort(key=lambda a: a['modified_at'], reverse=True)
    elif sort_by == 'status':
        filtered.sort(key=lambda a: (a['is_used'], -a['size_bytes']))

    context = {
        **admin.site.each_context(request),
        'title': 'Media & Storage Assets Manager',
        'assets': filtered,
        'stats': stats,
        'folders': folders,
        'current_tab': active_tab,
        'current_filter': filter_tab,
        'current_folder': folder_filter,
        'current_type': type_filter,
        'current_sort': sort_by,
        'search_query': search_query,
        'displayed_count': len(filtered),
        'has_permission': True,
    }
    return render(request, 'admin/core/assets_manager.html', context)


@superuser_required
@require_POST
def admin_asset_delete_view(request):
    """
    Safely deletes unused asset files or folders requested by superusers.
    Guarantees strict path traversal protection and locks core system files.
    """
    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    action = data.get('action', 'delete_file')
    base_dir = str(settings.BASE_DIR)
    media_root = str(settings.MEDIA_ROOT)
    static_dir = str(settings.STATICFILES_DIRS[0])
    staticfiles_dir = getattr(settings, 'STATIC_ROOT', os.path.join(base_dir, 'staticfiles'))

    # Allowed base directories for deletion (strictly isolated to user media)
    allowed_roots = [
        os.path.realpath(media_root),
    ]

    # Strictly forbidden subpaths
    forbidden_subpaths = [
        'static/image/logo',
        'static/image/Favicon-new',
        'static/image/favicon_io',
        'static/css',
        'static/js',
        'static/admin',
    ]

    def is_safe_path(target_path):
        target_real = os.path.realpath(target_path)
        # 1. Must be inside at least one allowed root
        is_inside_allowed = any(os.path.commonpath([target_real, allowed]) == allowed for allowed in allowed_roots)
        if not is_inside_allowed:
            return False, "Target is outside allowed media/static directories."

        # 2. Must not be inside forbidden subpaths
        rel_to_base = os.path.relpath(target_real, base_dir).replace('\\', '/')
        if any(rel_to_base.startswith(f) for f in forbidden_subpaths):
            return False, "Target is a protected system asset."

        # 3. Must not be code or DB
        ext = os.path.splitext(target_real)[1].lower()
        if ext in ['.py', '.sqlite3', '.json', '.html', '.css', '.js', '.sh', '.env']:
            return False, "Code or configuration files cannot be deleted."

        return True, ""

    deleted_count = 0
    reclaimed_bytes = 0

    if action == 'delete_file':
        rel_path = data.get('path', '').strip()
        if not rel_path:
            return JsonResponse({'success': False, 'error': 'No file path provided.'}, status=400)

        target_file = os.path.join(base_dir, rel_path)
        if not os.path.exists(target_file) or not os.path.isfile(target_file):
            return JsonResponse({'success': False, 'error': f'File not found: {rel_path}'}, status=404)

        safe, err_msg = is_safe_path(target_file)
        if not safe:
            return JsonResponse({'success': False, 'error': err_msg}, status=403)

        sz = os.path.getsize(target_file)
        try:
            os.remove(target_file)
            deleted_count += 1
            reclaimed_bytes += sz

            # Also remove from staticfiles mirror if present
            if target_file.startswith(static_dir) and staticfiles_dir and os.path.exists(staticfiles_dir):
                mirror_rel = os.path.relpath(target_file, static_dir)
                mirror_path = os.path.join(staticfiles_dir, mirror_rel)
                if os.path.exists(mirror_path):
                    try:
                        os.remove(mirror_path)
                        # Also check .gz
                        if os.path.exists(mirror_path + '.gz'):
                            os.remove(mirror_path + '.gz')
                    except Exception:
                        pass

        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Failed to delete file: {str(e)}'}, status=500)

    elif action == 'delete_multiple':
        paths = data.get('paths', [])
        if not paths:
            return JsonResponse({'success': False, 'error': 'No file paths provided.'}, status=400)

        errors = []
        for rel_path in paths:
            target_file = os.path.join(base_dir, rel_path.strip())
            if not os.path.exists(target_file) or not os.path.isfile(target_file):
                continue

            safe, err_msg = is_safe_path(target_file)
            if not safe:
                errors.append(f"{rel_path}: {err_msg}")
                continue

            sz = os.path.getsize(target_file)
            try:
                os.remove(target_file)
                deleted_count += 1
                reclaimed_bytes += sz

                # Clean staticfiles mirror
                if target_file.startswith(static_dir) and staticfiles_dir and os.path.exists(staticfiles_dir):
                    mirror_rel = os.path.relpath(target_file, static_dir)
                    mirror_path = os.path.join(staticfiles_dir, mirror_rel)
                    if os.path.exists(mirror_path):
                        try:
                            os.remove(mirror_path)
                            if os.path.exists(mirror_path + '.gz'):
                                os.remove(mirror_path + '.gz')
                        except Exception:
                            pass
            except Exception as e:
                errors.append(f"{rel_path}: {str(e)}")

        if deleted_count == 0 and errors:
            return JsonResponse({'success': False, 'error': '; '.join(errors)}, status=403)

    elif action == 'delete_folder':
        folder_path = data.get('folder_path', '').strip()
        if not folder_path:
            return JsonResponse({'success': False, 'error': 'No folder path provided.'}, status=400)

        target_dir = os.path.join(base_dir, folder_path)
        if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
            return JsonResponse({'success': False, 'error': f'Folder not found: {folder_path}'}, status=404)

        safe, err_msg = is_safe_path(target_dir)
        if not safe:
            return JsonResponse({'success': False, 'error': err_msg}, status=403)

        # Do not delete top-level folders
        rel_to_base = os.path.relpath(target_dir, base_dir).replace('\\', '/')
        if rel_to_base in ['media', 'static', 'static/image', 'static/video']:
            return JsonResponse({'success': False, 'error': 'Cannot delete root asset directory.'}, status=403)

        try:
            # Calculate reclaimed bytes inside folder
            folder_bytes = sum(os.path.getsize(os.path.join(r, f)) for r, d, files in os.walk(target_dir) for f in files)
            shutil.rmtree(target_dir)
            deleted_count += 1
            reclaimed_bytes += folder_bytes
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Failed to delete folder: {str(e)}'}, status=500)

    cache.delete('admin_unused_assets_count')
    reclaimed_mb = round(reclaimed_bytes / (1024 * 1024), 2)
    return JsonResponse({
        'success': True,
        'deleted_count': deleted_count,
        'reclaimed_bytes': reclaimed_bytes,
        'reclaimed_mb': reclaimed_mb,
        'message': f"Successfully removed {deleted_count} item(s), reclaiming {reclaimed_mb:.2f} MB storage."
    })


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN BACKUP & DATA MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@staff_member_required(login_url='admin:login')
def admin_backup_view(request):
    """
    Renders the Backup & Export Data Manager dashboard in Django admin.
    Displays live database records, file sizes, and provides buttons for
    exporting JSON snapshots, downloading SQLite db, syncing initial_data.json,
    and restoring backups.
    """
    from django.apps import apps
    import os
    import datetime

    sections = [
        {
            'title': 'Core Settings & Branding',
            'icon': '⚙️',
            'models': [
                ('Site Settings', apps.get_model('core', 'SiteSettings')),
                ('Navigation Items', apps.get_model('core', 'NavigationItem')),
                ('Popular Tags', apps.get_model('core', 'MegaMenuTag')),
                ('Social Links', apps.get_model('core', 'SocialLink')),
                ('Hero Stats', apps.get_model('core', 'StatItem')),
            ]
        },
        {
            'title': 'Projects & Portfolio Showcase',
            'icon': '🚀',
            'models': [
                ('Projects', apps.get_model('core', 'Project')),
                ('Project Categories', apps.get_model('core', 'ProjectCategory')),
                ('Technologies', apps.get_model('core', 'Technology')),
                ('Project Highlights', apps.get_model('core', 'ProjectHighlight')),
                ('Project Diagrams', apps.get_model('core', 'ProjectDiagram')),
                ('Timeline Phases', apps.get_model('core', 'ProjectTimelinePhase')),
                ('Project Features', apps.get_model('core', 'ProjectFeature')),
            ]
        },
        {
            'title': 'Blog & Technical Articles',
            'icon': '📝',
            'models': [
                ('Blog Posts', apps.get_model('core', 'BlogPost')),
                ('Blog Sections', apps.get_model('core', 'BlogSection')),
                ('Blog Categories', apps.get_model('core', 'BlogCategory')),
                ('Tags', apps.get_model('core', 'Tag')),
            ]
        },
        {
            'title': 'Free AI Tools & Utilities',
            'icon': '🛠️',
            'models': [
                ('AI Tools', apps.get_model('core', 'AITool')),
                ('Tool Categories', apps.get_model('core', 'ToolCategory')),
            ]
        },
        {
            'title': 'Bootcamps & Workshops',
            'icon': '🎓',
            'models': [
                ('Workshops', apps.get_model('core', 'WorkshopCard')),
                ('Curriculum Days', apps.get_model('core', 'WorkshopDay')),
                ('Student Enrollments', apps.get_model('core', 'WorkshopEnrollment')),
            ]
        },
        {
            'title': 'Services & Client Case Studies',
            'icon': '💼',
            'models': [
                ('Services', apps.get_model('core', 'Service')),
                ('Service Features', apps.get_model('core', 'ServiceFeature')),
                ('Case Studies', apps.get_model('core', 'CaseStudy')),
                ('Case Study Metrics', apps.get_model('core', 'CaseStudyMetric')),
                ('Pricing Plans', apps.get_model('core', 'PricingPlan')),
            ]
        },
        {
            'title': 'CRM, Leads & Inquiries',
            'icon': '📬',
            'models': [
                ('Contact Inquiries', apps.get_model('core', 'ContactInquiry')),
                ('Direct Messages', apps.get_model('core', 'ContactMessage')),
                ('Project Gate Leads', apps.get_model('core', 'ProjectGateLead')),
                ('Idea Proposals', apps.get_model('core', 'IdeaSubmission')),
                ('Chatbot Conversations', apps.get_model('core', 'ChatbotConversation')),
                ('Chatbot Messages', apps.get_model('core', 'ChatbotMessage')),
            ]
        },
        {
            'title': 'SEO, Operations & Feedback',
            'icon': '🔍',
            'models': [
                ('SEO Metadata', apps.get_model('core', 'SEOData')),
                ('301/302 Redirects', apps.get_model('core', 'Redirect')),
                ('Testimonials', apps.get_model('core', 'Testimonial')),
                ('FAQs', apps.get_model('core', 'FAQ')),
                ('FAQ Categories', apps.get_model('core', 'FAQCategory')),
                ('Admin Guide Notes', apps.get_model('core', 'AdminGuideNote')),
            ]
        },
    ]

    total_records = 0
    section_data = []
    for s in sections:
        items = []
        sec_total = 0
        for name, model_cls in s['models']:
            try:
                cnt = model_cls.objects.count()
            except Exception:
                cnt = 0
            sec_total += cnt
            items.append({'name': name, 'count': cnt})
        total_records += sec_total
        section_data.append({
            'title': s['title'],
            'icon': s['icon'],
            'total': sec_total,
            'items': items,
        })

    # Database file telemetry
    db_config = settings.DATABASES.get('default', {})
    db_engine = db_config.get('ENGINE', 'sqlite3').split('.')[-1]
    db_name = str(db_config.get('NAME', ''))
    db_size_kb = 0
    db_size_mb = 0
    db_exists = False
    db_modified = None
    if os.path.exists(db_name) and os.path.isfile(db_name):
        db_exists = True
        b = os.path.getsize(db_name)
        db_size_kb = round(b / 1024, 1)
        db_size_mb = round(b / (1024 * 1024), 2)
        db_modified = datetime.datetime.fromtimestamp(os.path.getmtime(db_name))

    # initial_data.json telemetry
    initial_path = os.path.join(settings.BASE_DIR, 'initial_data.json')
    initial_exists = os.path.exists(initial_path)
    initial_size_kb = round(os.path.getsize(initial_path) / 1024, 1) if initial_exists else 0
    initial_modified = datetime.datetime.fromtimestamp(os.path.getmtime(initial_path)) if initial_exists else None

    context = {
        'sections': section_data,
        'total_records': total_records,
        'db_engine': db_engine,
        'db_name': os.path.basename(db_name),
        'db_path': db_name,
        'db_size_kb': db_size_kb,
        'db_size_mb': db_size_mb,
        'db_exists': db_exists,
        'db_modified': db_modified,
        'initial_exists': initial_exists,
        'initial_size_kb': initial_size_kb,
        'initial_modified': initial_modified,
        'title': 'Database Backup & Export Manager',
    }
    return render(request, 'admin/backup.html', context)


@superuser_required
def admin_backup_download_json(request):
    """Generates and streams a JSON dump of all current models and settings."""
    import io
    from django.core.management import call_command
    from django.utils import timezone

    scope = request.GET.get('scope', 'all').lower()
    timestamp = timezone.now().strftime('%Y-%m-%d_%H-%M')
    
    scope_map = {
        'all': ['core', 'auth.user'],
        'settings': ['core.sitesettings', 'core.navigationitem', 'core.sociallink', 'core.statitem'],
        'projects': ['core.project', 'core.projectcategory', 'core.technology', 'core.projecthighlight', 'core.projectdiagram', 'core.projecttimelinephase', 'core.projectfeature'],
        'blog': ['core.blogpost', 'core.blogsection', 'core.blogcategory', 'core.tag'],
        'crm': ['core.contactinquiry', 'core.contactmessage', 'core.projectgatelead', 'core.ideasubmission', 'core.chatbotconversation', 'core.chatbotmessage'],
        'workshops': ['core.workshopcard', 'core.workshopday', 'core.workshopenrollment'],
    }

    target_apps = scope_map.get(scope, ['core', 'auth.user'])
    buf = io.StringIO()
    try:
        call_command('dumpdata', *target_apps, natural_foreign=True, natural_primary=True, indent=2, stdout=buf)
        data = buf.getvalue()
    except Exception as e:
        logger.exception("Failed to dumpdata for backup")
        return HttpResponse(f"Backup generation error: {str(e)}", status=500, content_type='text/plain')

    filename = f"projectshub_{scope}_backup_{timestamp}.json"
    response = HttpResponse(data, content_type='application/json; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@superuser_required
def admin_backup_download_db(request):
    """Directly streams the raw sqlite3 database file for download."""
    import os
    from django.http import FileResponse, Http404
    from django.conf import settings
    from django.utils import timezone

    db_config = settings.DATABASES.get('default', {})
    db_path = str(db_config.get('NAME', ''))

    if not os.path.exists(db_path) or not os.path.isfile(db_path):
        raise Http404("Database file not found or not on local filesystem.")

    timestamp = timezone.now().strftime('%Y-%m-%d_%H-%M')
    filename = f"projectshub_db_{timestamp}.sqlite3"
    response = FileResponse(open(db_path, 'rb'), content_type='application/x-sqlite3')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@superuser_required
@require_POST
def admin_backup_sync_initial(request):
    """
    Dumps all current models into initial_data.json so that
    deployments (Vercel, Railway, Docker) immediately boot with current data.
    """
    import os
    import io
    from django.core.management import call_command
    from django.conf import settings
    from django.contrib import messages
    from django.shortcuts import redirect

    initial_path = os.path.join(settings.BASE_DIR, 'initial_data.json')
    buf = io.StringIO()
    try:
        call_command('dumpdata', 'core', 'auth.user', natural_foreign=True, natural_primary=True, indent=2, stdout=buf)
        content = buf.getvalue()
        with open(initial_path, 'w', encoding='utf-8') as f:
            f.write(content)
        size_kb = round(os.path.getsize(initial_path) / 1024, 1)
        messages.success(
            request,
            f"Successfully updated initial_data.json ({size_kb} KB)! Your current site settings, projects, popular tags, and content are now synced for future deploys."
        )
    except Exception as e:
        logger.exception("Failed to sync initial_data.json")
        messages.error(request, f"Failed to sync initial_data.json: {str(e)}")

    return redirect('admin_backup')


@superuser_required
@require_POST
def admin_backup_restore(request):
    """Restores database from an uploaded JSON backup file using loaddata."""
    import os
    import tempfile
    from django.core.management import call_command
    from django.contrib import messages
    from django.shortcuts import redirect

    uploaded_file = request.FILES.get('backup_file')
    if not uploaded_file:
        messages.error(request, "No backup file uploaded.")
        return redirect('admin_backup')

    if not uploaded_file.name.endswith('.json'):
        messages.error(request, "Invalid file format. Please upload a .json backup file.")
        return redirect('admin_backup')

    fd, tmp_path = tempfile.mkstemp(suffix='.json')
    try:
        with os.fdopen(fd, 'wb') as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)
        
        call_command('loaddata', tmp_path)
        messages.success(request, f"Successfully restored database from '{uploaded_file.name}'!")
    except Exception as e:
        logger.exception("Failed to restore data from backup")
        messages.error(request, f"Restore failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return redirect('admin_backup')




