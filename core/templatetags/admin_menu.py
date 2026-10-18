"""
WordPress-style grouped admin sidebar.

Django's default sidebar lists every model of an app in one flat alphabetical
block (~45 items under "Core"). `admin_nav_groups` regroups those same
permission-filtered models into curated, labelled sections with icons, the way
wp-admin groups Posts / Pages / Appearance / Tools. It stays permission-aware
(it reads `admin.site.get_app_list(request)`, so a model the user can't see
never appears). Models that are normally edited inline stay available in an
"Advanced records" section instead of crowding the everyday navigation.
"""
from django import template
from django.contrib import admin

register = template.Library()

# (Section label, icon, [model object_names in display order]).
# object_name is the model class name, e.g. "BlogPost".
GROUPS = [
    ('Projects', '🚀', ['Project', 'ProjectFeature', 'ProjectHighlight', 'ProjectTimelinePhase',
                         'ProjectDiagram', 'ProjectImage', 'ProjectCategory', 'Technology']),
    ('Posts', '📝', ['BlogPost', 'BlogSection', 'BlogCategory', 'Tag']),
    ('Pages', '📄', ['Page']),
    ('AI Tools', '🛠️', ['AITool', 'ToolCategory']),
    ('Workshops', '🎓', ['WorkshopCard', 'WorkshopDay', 'WorkshopEnrollment']),
    ('AI Roadmap', '🗺️', ['RoadmapNode', 'RoadmapGroup', 'RoadmapTopic', 'RoadmapResource', 'RoadmapSettings']),
    ('Services', '💼', ['Service', 'ServiceFeature', 'CaseStudy', 'CaseStudyMetric',
                        'CaseStudyTechnology', 'PricingPlan', 'PricingFeature']),
    ('Feedback', '💬', ['Testimonial', 'FAQ', 'FAQCategory']),
    ('CRM & Leads', '📬', ['ContactInquiry', 'IdeaSubmission', 'ProjectGateLead', 'ContactMessage',
                           'ChatbotConversation', 'ChatbotMessage', 'ChatAgentStatus']),
    ('Appearance', '🎨', ['NavigationItem', 'MegaMenuTag', 'SocialLink', 'StatItem']),
    ('SEO & Redirects', '📈', ['SEOData', 'Redirect']),
    ('Media', '📁', ['Asset']),
    ('Guide', '📖', ['AdminGuideNote']),
    ('Settings', '⚙️', ['SiteSettings']),
    ('Users & Groups', '👥', ['User', 'Group', 'Permission']),
]


@register.simple_tag(takes_context=True)
def admin_nav_groups(context):
    request = context.get('request')
    user = getattr(request, 'user', None)
    if not request or not user or not user.is_active or not user.is_staff:
        return []

    # Flatten every model the user may access into object_name -> item.
    models = {}
    for app in admin.site.get_app_list(request):
        for m in app['models']:
            models[m['object_name']] = m

    inline_models = {
        inline.model.__name__
        for model_admin in admin.site._registry.values()
        for inline in model_admin.inlines
    }

    sections, used = [], set()
    for label, icon, names in GROUPS:
        everyday_names = [n for n in names if n in models and n not in inline_models]
        items = [models[n] for n in everyday_names]
        used.update(everyday_names)
        if items:
            sections.append({'label': label, 'icon': icon, 'items': items})

    leftover = [m for name, m in models.items() if name not in used]
    if leftover:
        sections.append({'label': 'Advanced records', 'icon': '▦',
                         'items': sorted(leftover, key=lambda m: m['name'])})
    return sections
