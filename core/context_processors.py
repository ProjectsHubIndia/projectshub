import sys
import django
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from core.models import (
    SiteSettings, NavigationItem, SocialLink, StatItem,
    Project, ProjectCategory, Technology,
    AITool, ToolCategory,
    Service, CaseStudy, PricingPlan, Testimonial,
    ContactInquiry, IdeaSubmission, WorkshopEnrollment, ProjectGateLead, ContactMessage,
    BlogPost, BlogCategory, Tag, FAQ, FAQCategory,
    SEOData, Redirect, ChatbotConversation, AdminGuideNote
)


from core.seo import get_seo_for_request


def site_context(request):
    """
    Supplies global site configuration, social links, navigation items,
    automated SEO metadata and schema, and admin analytics stats seamlessly.
    """
    try:
        settings_obj = SiteSettings.get_settings()
    except Exception:
        settings_obj = None

    try:
        social_links = list(SocialLink.objects.filter(is_active=True).order_by('order'))
    except Exception:
        social_links = []

    try:
        hero_stats = list(StatItem.objects.filter(section='hero', is_active=True).order_by('order'))
    except Exception:
        hero_stats = []

    try:
        all_nav = list(NavigationItem.objects.filter(is_active=True).order_by('order'))
        mega_work_items = [n for n in all_nav if n.group == 'our_work']
        mega_work_tags = [n for n in all_nav if n.group == 'popular_tags']
        mega_student_items = [n for n in all_nav if n.group == 'how_we_help_students']
        mega_business_items = [n for n in all_nav if n.group == 'how_we_help_business']
        primary_nav_items = [n for n in all_nav if n.group == 'main']
    except Exception:
        mega_work_items = []
        mega_work_tags = []
        mega_student_items = []
        mega_business_items = []
        primary_nav_items = []

    context = {
        'site_settings': settings_obj,
        'social_links': social_links,
        'hero_stats': hero_stats,
        'mega_work_items': mega_work_items,
        'mega_work_tags': mega_work_tags,
        'mega_student_items': mega_student_items,
        'mega_business_items': mega_business_items,
        'primary_nav_items': primary_nav_items,
    }

    # Automated SEO Engine for public pages
    if not request.path.startswith('/admin'):
        try:
            context['seo'] = get_seo_for_request(request)
        except Exception:
            pass

    if request.path.startswith('/admin'):
        try:
            User = get_user_model()

            # KPI & Aggregations
            total_projects = Project.objects.count()
            active_projects = Project.objects.filter(is_active=True).count()
            featured_projects = Project.objects.filter(featured=True).count()

            total_inquiries = ContactInquiry.objects.count()
            new_inquiries = ContactInquiry.objects.filter(status='new').count()
            converted_inquiries = ContactInquiry.objects.filter(status='converted').count()

            total_ideas = IdeaSubmission.objects.count()
            new_ideas = IdeaSubmission.objects.filter(status='new').count()

            total_tools = AITool.objects.count()
            free_tools = AITool.objects.filter(is_free=True).count()

            total_blogs = BlogPost.objects.count()
            published_blogs = BlogPost.objects.filter(is_published=True).count()

            total_enrollments = WorkshopEnrollment.objects.count()
            pending_enrollments = WorkshopEnrollment.objects.filter(status='pending').count()

            # Unused media & storage assets count (cached for 60s)
            cached_unused = cache.get('admin_unused_assets_count')
            if cached_unused is None:
                try:
                    from core.views import scan_all_assets
                    _, asset_stats, _ = scan_all_assets()
                    cached_unused = asset_stats.get('unused_count', 0)
                    cache.set('admin_unused_assets_count', cached_unused, 60)
                except Exception:
                    cached_unused = 0

            context['admin_stats'] = {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'featured_projects': featured_projects,
                'total_inquiries': total_inquiries,
                'new_inquiries': new_inquiries,
                'converted_inquiries': converted_inquiries,
                'total_ideas': total_ideas,
                'new_ideas': new_ideas,
                'total_tools': total_tools,
                'free_tools': free_tools,
                'total_blogs': total_blogs,
                'published_blogs': published_blogs,
                'total_case_studies': CaseStudy.objects.count(),
                'total_enrollments': total_enrollments,
                'pending_enrollments': pending_enrollments,
                'unused_assets_count': cached_unused,
            }

            # Live Model Count dictionary for grouped navigation badges
            context['model_counts'] = {
                'project': total_projects,
                'projectcategory': ProjectCategory.objects.count(),
                'technology': Technology.objects.count(),
                'aitool': total_tools,
                'toolcategory': ToolCategory.objects.count(),
                'service': Service.objects.count(),
                'casestudy': CaseStudy.objects.count(),
                'pricingplan': PricingPlan.objects.count(),
                'testimonial': Testimonial.objects.count(),
                'contactinquiry': total_inquiries,
                'ideasubmission': total_ideas,
                'workshopenrollment': total_enrollments,
                'projectgatelead': ProjectGateLead.objects.count(),
                'contactmessage': ContactMessage.objects.count(),
                'blogpost': total_blogs,
                'blogcategory': BlogCategory.objects.count(),
                'tag': Tag.objects.count(),
                'faq': FAQ.objects.count(),
                'faqcategory': FAQCategory.objects.count(),
                'sitesettings': 1,
                'navigationitem': NavigationItem.objects.count(),
                'sociallink': SocialLink.objects.count(),
                'statitem': StatItem.objects.count(),
                'seodata': SEOData.objects.count(),
                'redirect': Redirect.objects.count(),
                'user': User.objects.count(),
                'group': Group.objects.count(),
                'permission': Permission.objects.count(),
                'chatbotconversation': ChatbotConversation.objects.count(),
                'adminguidenote': AdminGuideNote.objects.count(),
            }

            # Recent CRM Activities & Content for WordPress Dashboard widgets
            context['recent_inquiries'] = ContactInquiry.objects.order_by('-created_at')[:5]
            context['recent_ideas'] = IdeaSubmission.objects.order_by('-created_at')[:3]
            context['recent_blogs'] = BlogPost.objects.order_by('-created_at')[:4]
            context['recent_projects'] = Project.objects.order_by('-created_at')[:4]

            # System & Platform Telemetry
            db_engine = settings.DATABASES.get('default', {}).get('ENGINE', 'sqlite3').split('.')[-1]
            cache_backend = settings.CACHES.get('default', {}).get('BACKEND', 'locmem').split('.')[-1]
            context['system_info'] = {
                'python_version': sys.version.split()[0],
                'django_version': django.get_version(),
                'db_engine': db_engine.replace('_', ' ').capitalize(),
                'cache_backend': cache_backend,
                'debug_mode': settings.DEBUG,
                'time_zone': getattr(settings, 'TIME_ZONE', 'UTC'),
            }
        except Exception:
            pass

    return context
