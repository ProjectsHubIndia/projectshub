import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import (
    Project, WorkshopCard, PricingPlan,
    ContactMessage, ProjectGateLead, IdeaSubmission, WorkshopEnrollment,
    BlogPost
)

def error_404(request, exception):
    return render(request, 'core/error404.html', status=404)

def error_500(request):
    return render(request, 'core/error500.html', status=500)

def ai_roadmap(request):
    return render(request, 'core/ai_roadmap.html')

def ai_development(request):
    return render(request, 'core/ai_development.html')

def ai_automation(request):
    return render(request, 'core/ai_automation.html')

def ai_integration(request):
    return render(request, 'core/ai_integration.html')

def industries(request):
    return render(request, 'core/industries.html')
    
def case_studies_page(request):
    return render(request, 'core/case_studies.html')

def tools_page(request):
    return redirect('https://tools.projectshub.co.in/')

def blog_page(request):
    """Blog listing page."""
    posts = BlogPost.objects.filter(is_active=True)
    return render(request, 'core/blog.html', {'posts': posts})


def blog_detail(request, slug):
    """Blog post detail page."""
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
    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ── Pages ──────────────────────────────────────────────────────────────────────

def index(request):
    """Homepage — passes dynamic data to the template."""
    index_projects = Project.objects.filter(
        is_active=True, show_on_index=True
    ).order_by('order', '-created_at')
    pricing_plans = PricingPlan.objects.filter(
        is_active=True
    ).prefetch_related('features')
    context = {
        'index_projects': index_projects,
        'pricing_plans': pricing_plans,
    }
    return render(request, 'core/index.html', context)


def projects_page(request):
    """All projects page."""
    projects = Project.objects.filter(
        is_active=True
    ).order_by('order', '-created_at')
    context = {'projects': projects}
    return render(request, 'core/projects.html', context)


def project_detail(request, project_id):
    """Project detail page."""
    project = get_object_or_404(
        Project.objects.prefetch_related(
            'detail_images', 'highlights', 'diagrams',
            'timeline_phases', 'price_features',
        ),
        id=project_id, is_active=True
    )
    related_projects = (
        Project.objects
        .filter(is_active=True, category=project.category)
        .exclude(id=project_id)
        .order_by('order', '-created_at')[:3]
    )
    context = {
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'core/project_detail.html', context)


def workshop_page(request):
    """Workshop listing page — shows all active workshops."""
    workshops = WorkshopCard.objects.filter(
        is_active=True
    ).prefetch_related('days').order_by('order', '-created_at')
    featured = next((w for w in workshops if w.is_featured), None) or next(iter(workshops), None)
    context = {
        'workshops': workshops,
        'workshop': featured,
    }
    return render(request, 'core/workshop.html', context)


def workshop_detail(request, workshop_id):
    """Workshop detail page — full info with curriculum."""
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
    """Workshop day detail page — single day curriculum."""
    workshop = get_object_or_404(
        WorkshopCard.objects.prefetch_related('days'),
        id=workshop_id, is_active=True
    )
    day = get_object_or_404(workshop.days, day_number=day_number)
    days = list(workshop.days.all())
    current_idx = next((i for i, d in enumerate(days) if d.day_number == day_number), 0)
    prev_day = days[current_idx - 1] if current_idx > 0 else None
    next_day = days[current_idx + 1] if current_idx < len(days) - 1 else None
    context = {
        'workshop': workshop,
        'day': day,
        'days': days,
        'prev_day': prev_day,
        'next_day': next_day,
        'total_days': len(days),
    }
    return render(request, 'core/workshop-day.html', context)


# ── Form Endpoints ─────────────────────────────────────────────────────────────

def _parse_request_data(request):
    """Parse JSON or form-encoded POST data."""
    if request.content_type and 'application/json' in request.content_type:
        return json.loads(request.body)
    return request.POST


@require_POST
def contact_submit(request):
    """Handle contact form submission."""
    try:
        data = _parse_request_data(request)
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        errors = {}
        if not full_name:
            errors['full_name'] = 'Full name is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not message:
            errors['message'] = 'Message is required.'

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        ContactMessage.objects.create(
            full_name=full_name,
            email=email,
            subject=subject,
            message=message,
            ip_address=get_client_ip(request),
        )
        return JsonResponse({
            'success': True,
            'message': "Thanks! We'll get back to you within 24 hours."
        })
    except Exception:
        return JsonResponse(
            {'success': False, 'message': 'Something went wrong. Please try again.'},
            status=500
        )


@require_POST
def gate_submit(request):
    """Handle the project gate modal form (lead capture)."""
    try:
        data = _parse_request_data(request)
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        college_or_org = data.get('college_or_org', '').strip()

        errors = {}
        if not full_name:
            errors['full_name'] = 'Name is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not college_or_org:
            errors['college_or_org'] = 'College / organization is required.'

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
        return JsonResponse(
            {'success': False, 'message': 'Something went wrong.'},
            status=500
        )


@require_POST
def idea_submit(request):
    """Handle the 'Share Your Idea' modal form submission."""
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
        return JsonResponse(
            {'success': False, 'message': 'Something went wrong. Please try again.'},
            status=500
        )


@require_POST
def enroll_submit(request):
    """Handle workshop enrollment form submission."""
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

        # Resolve workshop if id provided
        workshop = None
        if workshop_id:
            try:
                workshop = WorkshopCard.objects.get(id=workshop_id, is_active=True)
            except WorkshopCard.DoesNotExist:
                pass

        # Prevent duplicate enrollment per workshop
        if workshop:
            obj, created = WorkshopEnrollment.objects.get_or_create(
                workshop=workshop,
                email=email,
                defaults={
                    'full_name': full_name,
                    'phone': phone,
                    'experience': experience,
                    'referral': referral,
                    'message': message,
                    'agreed_to_terms': agreed,
                    'ip_address': get_client_ip(request),
                }
            )
            if not created:
                return JsonResponse({
                    'success': False,
                    'message': "You're already enrolled in this workshop!"
                }, status=400)
        else:
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

        return JsonResponse({
            'success': True,
            'message': "Enrollment successful! Check your email for confirmation."
        })
    except Exception:
        return JsonResponse(
            {'success': False, 'message': 'Something went wrong. Please try again.'},
            status=500
        )


# ── JSON API Endpoints ─────────────────────────────────────────────────────────

def api_projects(request):
    """JSON endpoint — returns active projects."""
    qs = Project.objects.filter(is_active=True)
    if request.GET.get('index_only'):
        qs = qs.filter(show_on_index=True)

    projects_data = []
    for p in qs:
        projects_data.append({
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'image': p.get_image_src(),
            'tags': p.get_tags_list(),
            'category': p.category,
            'project_url': p.project_url,
            'youtube_url': p.youtube_url,
            'show_on_index': p.show_on_index,
            'detail_url': f'/projects/{p.id}/',
        })
    return JsonResponse({'projects': projects_data})


def api_pricing(request):
    """JSON endpoint — returns active pricing plans with features."""
    plans = PricingPlan.objects.filter(
        is_active=True
    ).prefetch_related('features')
    data = []
    for plan in plans:
        data.append({
            'id': plan.id,
            'name': plan.name,
            'icon_type': plan.icon_type,
            'description': plan.description,
            'is_free': plan.is_free,
            'monthly_price': str(plan.monthly_price),
            'yearly_price': str(plan.yearly_price),
            'monthly_original': str(plan.monthly_original),
            'yearly_original': str(plan.yearly_original),
            'is_featured': plan.is_featured,
            'cta_label': plan.cta_label,
            'features': [f.feature for f in plan.features.all()],
        })
    return JsonResponse({'plans': data})


def api_workshops(request):
    """JSON endpoint — returns active workshops with days."""
    workshops = WorkshopCard.objects.filter(
        is_active=True
    ).prefetch_related('days')
    data = []
    for w in workshops:
        days = [
            {
                'day_number': d.day_number,
                'title': d.title,
                'date_label': d.date_label,
                'description': d.description,
                'outcome': d.outcome,
            }
            for d in w.days.all()
        ]
        data.append({
            'id': w.id,
            'title': w.title,
            'subtitle': w.subtitle,
            'description': w.description,
            'date': w.date,
            'time': w.time,
            'seats': w.seats,
            'mode': w.mode,
            'price': str(w.price),
            'price_label': w.price_label,
            'enroll_url': w.enroll_url,
            'is_featured': w.is_featured,
            'days': days,
        })
    return JsonResponse({'workshops': data})


def api_blog(request):
    """JSON endpoint — returns active blog posts."""
    posts = BlogPost.objects.filter(is_active=True)
    data = [
        {
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'category': p.category,
            'category_label': p.get_category_display(),
            'excerpt': p.excerpt,
            'image': p.get_image_src(),
            'emoji': p.emoji,
            'read_time': p.read_time,
            'published_at': p.published_at.isoformat(),
            'author': p.author_name,
            'is_featured': p.is_featured,
            'detail_url': f'/blog/{p.slug}/',
        }
        for p in posts
    ]
    return JsonResponse({'posts': data})
