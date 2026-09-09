from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.index, name='index'),
    path('projects/', views.projects_page, name='projects'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail_slug'),
    path('workshop/', views.workshop_page, name='workshop'),
    path('workshop/<int:workshop_id>/', views.workshop_detail, name='workshop_detail'),
    path('workshop/<int:workshop_id>/day/<int:day_number>/', views.workshop_day_detail, name='workshop_day_detail'),

    # Case Studies
    path('case-studies/', views.case_studies_page, name='case_studies'),

    # Tools
    path('tools/', views.tools_page, name='tools'),

    # AI Road Map
    path('ai-roadmap/', views.ai_roadmap, name='ai_roadmap'),

    # Services
    path('services/ai-development/', views.ai_development, name='ai_development'),
    path('services/ai-automation/', views.ai_automation, name='ai_automation'),
    path('services/ai-integration/', views.ai_integration, name='ai_integration'),

    # Industries
    path('industries/', views.industries, name='industries'),

    # Blog
    path('blog/', views.blog_page, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),

    # Form endpoints
    path('contact/', views.contact_submit, name='contact_submit'),
    path('gate/', views.gate_submit, name='gate_submit'),
    path('idea/', views.idea_submit, name='idea_submit'),
    path('enroll/', views.enroll_submit, name='enroll_submit'),

    # JSON API
    path('api/captcha/', views.api_captcha, name='api_captcha'),
    path('api/projects/', views.api_projects, name='api_projects'),
    path('api/pricing/', views.api_pricing, name='api_pricing'),
    path('api/workshops/', views.api_workshops, name='api_workshops'),
    path('api/blog/', views.api_blog, name='api_blog'),
    path('api/chatbot/message/', views.api_chatbot_message, name='api_chatbot_message'),
    path('api/chatbot/history/', views.api_chatbot_history, name='api_chatbot_history'),

    # Legal
    path('terms/', views.terms, name='terms'),
    path('refund/', views.refund, name='refund'),
    path('privacy/', views.privacy, name='privacy'),
    path('sitemap/', views.html_sitemap, name='html_sitemap'),

    # SEO
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
]
