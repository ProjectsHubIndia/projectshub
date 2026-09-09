import json
import logging
import random
import html
import re
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.core import signing
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required

from .models import (
    SiteSettings, NavigationItem, SocialLink, StatItem,
    ProjectCategory, Technology, Project, ProjectImage, ProjectHighlight,
    ProjectDiagram, ProjectTimelinePhase, ProjectFeature,
    ToolCategory, AITool,
    Service, ServiceFeature,
    CaseStudy, CaseStudyMetric,
    Testimonial, FAQCategory, FAQ,
    BlogCategory, Tag, BlogPost, BlogSection,
    ContactInquiry, ContactMessage, ProjectGateLead,
    IdeaSubmission, WorkshopCard, WorkshopDay, WorkshopEnrollment,
    PricingPlan, PricingFeature,
    SEOData, Redirect,
    ChatbotConversation, ChatbotMessage,
    AdminGuideNote
)

logger = logging.getLogger(__name__)


def error_404(request, exception=None):
    return render(request, 'core/error404.html', status=404)


def error_500(request):
    return render(request, 'core/error500.html', status=500)


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
            try:
                token_captcha = signing.loads(captcha_token, salt='captcha-salt', max_age=600)
            except Exception:
                token_captcha = None

        if not catch_code:
            errors['catch_code'] = 'Catch code (security verification) is required.'
        elif catch_code != session_captcha and catch_code != token_captcha:
            errors['catch_code'] = 'Invalid catch code. Please enter the characters shown in the image.'

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # Clear used session captcha
        if 'contact_captcha' in request.session:
            del request.session['contact_captcha']
            request.session.modified = True

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
    qs = Project.objects.filter(is_active=True)
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
    lines = [
        'User-agent: *',
        'Allow: /',
        '',
        'Disallow: /admin/',
        'Disallow: /gate/',
        'Disallow: /idea/',
        'Disallow: /enroll/',
        'Disallow: /api/',
        '',
        'Sitemap: https://projectshub.co.in/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def sitemap_xml(request):
    base_url = "https://projectshub.co.in"
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

        page_url = data.get('page_url', '').strip() or request.META.get('HTTP_REFERER', '/')
        ip_addr = get_client_ip(request)
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


