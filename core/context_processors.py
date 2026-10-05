import sys
import django
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from core.models import (
    SiteSettings, NavigationItem, MegaMenuTag, SocialLink, StatItem,
    Project, ProjectCategory, Technology, ProjectImage, ProjectHighlight,
    ProjectDiagram, ProjectTimelinePhase, ProjectFeature,
    AITool, ToolCategory,
    Service, ServiceFeature, CaseStudy, CaseStudyMetric, CaseStudyTechnology,
    PricingPlan, PricingFeature, Testimonial,
    ContactInquiry, IdeaSubmission, WorkshopCard, WorkshopDay, WorkshopEnrollment, ProjectGateLead, ContactMessage,
    BlogPost, BlogSection, BlogCategory, Tag, FAQ, FAQCategory,
    SEOData, Redirect, ChatbotConversation, ChatbotMessage, AdminGuideNote,
    Page
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

    # Dynamic Domain and Site URL (automatically detected from incoming request)
    site_url = ""
    current_domain = ""
    if request:
        try:
            site_url = request.build_absolute_uri('/').rstrip('/')
            current_domain = request.get_host()
        except Exception:
            pass
    if not site_url:
        site_url = getattr(settings, 'SITE_URL', 'https://projectshub.co.in').rstrip('/')
        current_domain = getattr(settings, 'SITE_DOMAIN', 'projectshub.co.in')

    scheme = 'https' if (request and request.is_secure()) else 'http'

    context = {
        'site_settings': settings_obj,
        'social_links': social_links,
        'hero_stats': hero_stats,
        'mega_work_items': mega_work_items,
        'mega_work_tags': mega_work_tags,
        'mega_student_items': mega_student_items,
        'mega_business_items': mega_business_items,
        'primary_nav_items': primary_nav_items,
        'site_url': site_url,
        'current_domain': current_domain,
        'site_scheme': scheme,
        'seo': {},
    }

    # Automated SEO Engine for public pages
    if not request.path.startswith('/admin'):
        try:
            seo_data = get_seo_for_request(request)
            if seo_data:
                context['seo'] = seo_data
        except Exception:
            pass

    if request.path.startswith('/admin'):
        try:
            User = get_user_model()

            # KPI & Aggregations (Cached for 300s to avoid 40+ COUNT queries per admin request)
            def compute_admin_stats():
                return {
                    'total_projects': Project.objects.count(),
                    'active_projects': Project.objects.filter(is_active=True).count(),
                    'featured_projects': Project.objects.filter(featured=True).count(),
                    'total_highlights': ProjectHighlight.objects.count(),
                    'total_features': ProjectFeature.objects.count(),
                    'total_timeline_phases': ProjectTimelinePhase.objects.count(),
                    'total_inquiries': ContactInquiry.objects.count(),
                    'new_inquiries': ContactInquiry.objects.filter(status='new').count(),
                    'converted_inquiries': ContactInquiry.objects.filter(status='converted').count(),
                    'total_messages': ContactMessage.objects.count(),
                    'total_leads': ProjectGateLead.objects.count(),
                    'total_ideas': IdeaSubmission.objects.count(),
                    'new_ideas': IdeaSubmission.objects.filter(status='new').count(),
                    'total_tools': AITool.objects.count(),
                    'free_tools': AITool.objects.filter(is_free=True).count(),
                    'total_blogs': BlogPost.objects.count(),
                    'total_sections': BlogSection.objects.count(),
                    'published_blogs': BlogPost.objects.filter(is_published=True).count(),
                    'total_case_studies': CaseStudy.objects.count(),
                    'total_services': Service.objects.count(),
                    'total_plans': PricingPlan.objects.count(),
                    'total_pricing_features': PricingFeature.objects.count(),
                    'total_workshops': WorkshopCard.objects.count(),
                    'total_enrollments': WorkshopEnrollment.objects.count(),
                    'pending_enrollments': WorkshopEnrollment.objects.filter(status='pending').count(),
                    'total_chats': ChatbotConversation.objects.count(),
                    'total_chat_messages': ChatbotMessage.objects.count(),
                    'total_testimonials': Testimonial.objects.count(),
                    'total_faqs': FAQ.objects.count(),
                    'total_seo': SEOData.objects.count(),
                    'total_redirects': Redirect.objects.count(),
                    'unused_assets_count': cache.get('admin_unused_assets_count', 0),
                }

            context['admin_stats'] = cache.get_or_set('admin_kpi_stats', compute_admin_stats, 60)

            # Live Model Count dictionary for grouped navigation badges (Cached for 60s)
            def compute_model_counts():
                return {
                    'project': Project.objects.count(),
                    'projectcategory': ProjectCategory.objects.count(),
                    'technology': Technology.objects.count(),
                    'projectimage': ProjectImage.objects.count(),
                    'projecthighlight': ProjectHighlight.objects.count(),
                    'projectdiagram': ProjectDiagram.objects.count(),
                    'projecttimelinephase': ProjectTimelinePhase.objects.count(),
                    'projectfeature': ProjectFeature.objects.count(),
                    'aitool': AITool.objects.count(),
                    'toolcategory': ToolCategory.objects.count(),
                    'service': Service.objects.count(),
                    'servicefeature': ServiceFeature.objects.count(),
                    'casestudy': CaseStudy.objects.count(),
                    'casestudymetric': CaseStudyMetric.objects.count(),
                    'casestudytechnology': CaseStudyTechnology.objects.count(),
                    'pricingplan': PricingPlan.objects.count(),
                    'pricingfeature': PricingFeature.objects.count(),
                    'testimonial': Testimonial.objects.count(),
                    'contactinquiry': ContactInquiry.objects.count(),
                    'ideasubmission': IdeaSubmission.objects.count(),
                    'workshopcard': WorkshopCard.objects.count(),
                    'workshopday': WorkshopDay.objects.count(),
                    'workshopenrollment': WorkshopEnrollment.objects.count(),
                    'projectgatelead': ProjectGateLead.objects.count(),
                    'contactmessage': ContactMessage.objects.count(),
                    'blogpost': BlogPost.objects.count(),
                    'page': Page.objects.count(),
                    'blogsection': BlogSection.objects.count(),
                    'blogcategory': BlogCategory.objects.count(),
                    'tag': Tag.objects.count(),
                    'faq': FAQ.objects.count(),
                    'faqcategory': FAQCategory.objects.count(),
                    'sitesettings': 1,
                    'navigationitem': NavigationItem.objects.count(),
                    'megamenutag': MegaMenuTag.objects.count(),
                    'sociallink': SocialLink.objects.count(),
                    'statitem': StatItem.objects.count(),
                    'seodata': SEOData.objects.count(),
                    'redirect': Redirect.objects.count(),
                    'user': User.objects.count(),
                    'group': Group.objects.count(),
                    'permission': Permission.objects.count(),
                    'chatbotconversation': ChatbotConversation.objects.count(),
                    'chatbotmessage': ChatbotMessage.objects.count(),
                    'adminguidenote': AdminGuideNote.objects.count(),
                }

            context['model_counts'] = cache.get_or_set('admin_model_counts', compute_model_counts, 60)

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
