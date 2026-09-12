"""
core/seo.py — Automated SEO & Schema.org JSON-LD Engine for ProjectsHub.
Provides dynamic, best-practice meta tags, OpenGraph, Twitter Cards,
robots index control, and multi-entity Schema.org structured data.
"""

import json
from urllib.parse import urlparse
from django.conf import settings
from django.utils.html import strip_tags
from core.models import SEOData

DEFAULT_DOMAIN = "https://projectshub.co.in"
DEFAULT_OG_IMAGE = "/static/image/favicon_io/og-image.png"
DEFAULT_ROBOTS = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"


def get_base_url(request=None):
    if request:
        try:
            return request.build_absolute_uri('/').rstrip('/')
        except Exception:
            pass
    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    if site_url:
        return site_url
    return DEFAULT_DOMAIN.rstrip('/')


def build_organization_schema(base_url):
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "ProjectsHub",
        "alternateName": "AI ProjectsHub",
        "url": base_url,
        "logo": f"{base_url}/static/image/logo/projectshub-logo-dark.png",
        "description": "Production-grade AI solutions, curated ML systems, and 1-on-1 mentorship for developers and modern businesses.",
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+91-9213472954",
            "contactType": "customer service",
            "availableLanguage": ["English", "Hindi"]
        },
        "sameAs": [
            "https://github.com/ProjectsHub",
            "https://linkedin.com/company/projectshub",
            "https://instagram.com/projectshub.ai"
        ]
    }


def build_website_schema(base_url):
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "ProjectsHub",
        "url": base_url,
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{base_url}/projects/?search={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    }


def build_breadcrumbs_schema(items, base_url):
    """
    items: list of (name, path) tuples
    """
    elements = []
    for idx, (name, path) in enumerate(items, start=1):
        elements.append({
            "@type": "ListItem",
            "position": idx,
            "name": name,
            "item": f"{base_url}{path}" if path.startswith('/') else path
        })
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": elements
    }


def get_seo_for_request(request, view_context=None):
    """
    Main SEO entry point. Evaluates request.path, resolves any explicit SEOData override,
    or dynamically synthesizes the highest-quality metadata and Schema.org structured data.
    """
    path = request.path if request else '/'
    base_url = get_base_url(request)
    full_url = f"{base_url}{path}"
    
    # 1. Check for explicit database override in SEOData
    custom_seo = None
    try:
        custom_seo = SEOData.objects.filter(path=path).first()
        if not custom_seo and path.endswith('/') and len(path) > 1:
            custom_seo = SEOData.objects.filter(path=path[:-1]).first()
    except Exception:
        pass

    # Defaults
    meta_title = "ProjectsHub — Enterprise AI, Real-World Projects & Developer Tools"
    meta_description = (
        "Empowering developers and modern enterprises with production-ready AI systems, "
        "curated machine learning pipelines, and intensive 1-on-1 mentorship."
    )
    canonical_url = full_url
    og_title = ""
    og_description = ""
    og_image = f"{base_url}{DEFAULT_OG_IMAGE}"
    og_type = "website"
    robots = DEFAULT_ROBOTS
    is_indexable = True
    schemas = []

    # 2. Dynamic Route & Model Analysis
    # A. HOMEPAGE
    if path in ['/', '']:
        meta_title = "ProjectsHub — From Ideas to AI-Powered Products"
        meta_description = (
            "Explore 50+ production-grade AI & ML projects, free developer utilities, "
            "and expert-led 3-day bootcamps to build scalable intelligence."
        )
        schemas.append(build_organization_schema(base_url))
        schemas.append(build_website_schema(base_url))

    # B. PROJECTS CATALOG
    elif path.startswith('/projects/') and path == '/projects/':
        meta_title = "Curated AI Projects & Production Architectures | ProjectsHub"
        meta_description = (
            "Browse 50+ production-ready AI, ML, computer vision, and full-stack Django "
            "projects complete with source code, live demos, and documentation."
        )
        schemas.append(build_breadcrumbs_schema([("Home", "/"), ("Projects", "/projects/")], base_url))

    # C. PROJECT DETAIL
    elif path.startswith('/projects/') and view_context and 'project' in view_context:
        prj = view_context['project']
        meta_title = f"{prj.title} — AI Project Showcase | ProjectsHub"
        clean_desc = strip_tags(prj.description or prj.title)[:155].strip()
        meta_description = clean_desc if clean_desc else f"Explore {prj.title} with code, architecture, and live deployment."
        og_type = "product"
        if getattr(prj, 'image', None):
            og_image = f"{base_url}{prj.image.url}"
        
        schemas.append(build_breadcrumbs_schema([
            ("Home", "/"),
            ("Projects", "/projects/"),
            (prj.title, prj.get_absolute_url() if hasattr(prj, 'get_absolute_url') else path)
        ], base_url))
        schemas.append({
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": prj.title,
            "operatingSystem": "Web, Linux, Docker, Python 3.12",
            "applicationCategory": getattr(prj.category, 'name', 'DeveloperApplication') if getattr(prj, 'category', None) else "DeveloperApplication",
            "description": meta_description,
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.9",
                "reviewCount": "48"
            }
        })

    # D. BLOG LISTING
    elif path == '/blog/':
        meta_title = "AI Insights, Engineering Guides & Tutorials | ProjectsHub Blog"
        meta_description = (
            "Read cutting-edge tutorials on LLM fine-tuning, computer vision architectures, "
            "FastAPI scalability, and career roadmaps by senior AI practitioners."
        )
        schemas.append(build_breadcrumbs_schema([("Home", "/"), ("Blog", "/blog/")], base_url))

    # E. BLOG POST DETAIL
    elif path.startswith('/blog/') and view_context and 'post' in view_context:
        post = view_context['post']
        meta_title = f"{post.title} | ProjectsHub Blog"
        clean_desc = strip_tags(post.excerpt or post.content or post.title)[:155].strip()
        meta_description = clean_desc
        og_type = "article"
        if getattr(post, 'featured_image', None):
            og_image = f"{base_url}{post.featured_image.url}"
        
        schemas.append(build_breadcrumbs_schema([
            ("Home", "/"),
            ("Blog", "/blog/"),
            (post.title, post.get_absolute_url() if hasattr(post, 'get_absolute_url') else path)
        ], base_url))
        schemas.append({
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post.title,
            "description": meta_description,
            "datePublished": post.created_at.isoformat() if hasattr(post, 'created_at') and post.created_at else "",
            "dateModified": post.updated_at.isoformat() if hasattr(post, 'updated_at') and post.updated_at else "",
            "author": {
                "@type": "Person",
                "name": getattr(post.author, 'get_full_name', lambda: 'ProjectsHub AI Team')() or 'ProjectsHub AI Team'
            },
            "publisher": {
                "@type": "Organization",
                "name": "ProjectsHub",
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{base_url}/static/image/logo/projectshub-logo-dark.png"
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": full_url
            }
        })

    # F. AI TOOLS DIRECTORY
    elif path == '/tools/':
        meta_title = "Free AI Developer Tools & Productivity Suites | ProjectsHub"
        meta_description = (
            "Explore curated developer tools: prompt optimizers, model latency testers, "
            "token calculators, and utility suites for modern engineering."
        )
        schemas.append(build_breadcrumbs_schema([("Home", "/"), ("AI Tools", "/tools/")], base_url))

    # G. 3-DAY WORKSHOP / BOOTCAMP
    elif '/workshop' in path:
        meta_title = "3-Day Live Full-Stack AI Bootcamp | ProjectsHub"
        meta_description = (
            "Intensive hands-on live coding workshop: Build production LLM systems, "
            "FastAPI microservices, and deploy real AI applications in 72 hours."
        )
        schemas.append(build_breadcrumbs_schema([("Home", "/"), ("Workshop", "/workshop/")], base_url))
        schemas.append({
            "@context": "https://schema.org",
            "@type": "Course",
            "name": "3-Day Live Full-Stack AI Bootcamp",
            "description": meta_description,
            "provider": {
                "@type": "Organization",
                "name": "ProjectsHub",
                "sameAs": base_url
            },
            "educationalCredentialAwarded": "Certificate of Completion",
            "offers": {
                "@type": "Offer",
                "price": "999",
                "priceCurrency": "INR",
                "category": "Paid"
            }
        })

    # H. CASE STUDIES
    elif path.startswith('/case-studies'):
        meta_title = "Real-World AI Case Studies & Client Success Stories | ProjectsHub"
        meta_description = (
            "Detailed technical case studies showcasing computer vision deployments, "
            "LLM workflow automation, and measurable enterprise ROI."
        )
        schemas.append(build_breadcrumbs_schema([("Home", "/"), ("Case Studies", "/case-studies/")], base_url))

    # I. AI ROADMAP
    elif '/roadmap' in path:
        meta_title = "The 2026 AI Engineer Career Road Map | ProjectsHub"
        meta_description = (
            "A comprehensive step-by-step career path from foundational Python "
            "to advanced deep learning, LLMs, fine-tuning, and MLOps."
        )
        schemas.append(build_breadcrumbs_schema([("Home", "/"), ("AI Roadmap", "/ai-roadmap/")], base_url))

    # J. LEGAL / TERMS / PRIVACY
    elif 'privacy' in path:
        meta_title = "Privacy Policy | ProjectsHub"
        meta_description = "Learn how ProjectsHub respects your personal data, privacy rights, and adheres to strict security standards."
    elif 'terms' in path:
        meta_title = "Terms of Service | ProjectsHub"
        meta_description = "Read the ProjectsHub terms of service, platform usage conditions, and developer policies."
    elif 'refund' in path:
        meta_title = "Refund & Cancellation Policy | ProjectsHub"
        meta_description = "Read about ProjectsHub refund terms, workshop cancellation policies, and satisfaction guarantees."

    # K. CONTACT US
    elif path == '/contact/' or path.startswith('/contact/'):
        meta_title = "Contact Us | Get in Touch With ProjectsHub AI Engineers"
        meta_description = (
            "Have an AI project idea, questions about our capstone projects, or need 1-on-1 mentorship? "
            "Get in touch with the ProjectsHub engineering team. We reply within 24 hours."
        )
        schemas.append(build_breadcrumbs_schema([("Home", "/"), ("Contact Us", "/contact/")], base_url))
        schemas.append({
            "@context": "https://schema.org",
            "@type": "ContactPage",
            "name": "Contact ProjectsHub",
            "description": meta_description,
            "url": full_url,
        })

    # 3. Apply custom database override if found
    if custom_seo:
        if custom_seo.meta_title:
            meta_title = custom_seo.meta_title
        if custom_seo.meta_description:
            meta_description = custom_seo.meta_description
        if custom_seo.canonical_url:
            raw_canonical = custom_seo.canonical_url.strip()
            if raw_canonical.startswith('/'):
                canonical_url = f"{base_url}{raw_canonical}"
            else:
                parsed_c = urlparse(raw_canonical)
                internal_hosts = {'projectshub.co.in', 'www.projectshub.co.in', 'localhost', '127.0.0.1'}
                if request:
                    internal_hosts.add(request.get_host().split(':')[0])
                if parsed_c.netloc.split(':')[0] in internal_hosts or not parsed_c.netloc:
                    path_part = parsed_c.path if parsed_c.path else '/'
                    if parsed_c.query:
                        path_part += f"?{parsed_c.query}"
                    canonical_url = f"{base_url}{path_part}"
                else:
                    canonical_url = raw_canonical
        if custom_seo.og_title:
            og_title = custom_seo.og_title
        if custom_seo.og_description:
            og_description = custom_seo.og_description
        if custom_seo.og_image:
            try:
                og_image = f"{base_url}{custom_seo.og_image.url}"
            except Exception:
                pass
        if custom_seo.robots:
            robots = custom_seo.robots
        is_indexable = custom_seo.is_indexable
        if not is_indexable:
            robots = "noindex, nofollow"
        if custom_seo.custom_json_ld:
            try:
                custom_parsed = json.loads(custom_seo.custom_json_ld)
                schemas = [custom_parsed]
            except Exception:
                pass

    if not og_title:
        og_title = meta_title
    if not og_description:
        og_description = meta_description

    # Consolidate schema JSON-LD script tags
    schema_json_strings = [
        f'<script type="application/ld+json">\n{json.dumps(s, indent=2)}\n</script>'
        for s in schemas
    ]
    schema_markup = "\n".join(schema_json_strings)

    return {
        'meta_title': meta_title,
        'meta_description': meta_description,
        'canonical_url': canonical_url,
        'robots': robots,
        'is_indexable': is_indexable,
        'og_type': og_type,
        'og_title': og_title,
        'og_description': og_description,
        'og_image': og_image,
        'og_url': canonical_url,
        'twitter_card': 'summary_large_image',
        'twitter_title': og_title,
        'twitter_description': og_description,
        'twitter_image': og_image,
        'schemas': schemas,
        'schema_json': schema_markup,
        'schema_types': [s.get('@type', 'Thing') for s in schemas],
    }


def get_all_site_routes_seo_status(request=None):
    """
    Audits all primary site routes and models for the SEO & Index Status Telemetry Dashboard.
    Returns structured list of routes with indexability status, title score, description score,
    canonical validity, and schema types.
    """
    base_url = get_base_url(request)

    class MockRequest:
        def __init__(self, path):
            self.path = path
        def build_absolute_uri(self, p='/'):
            return f"{base_url}{p}"
        def get_host(self):
            return base_url.replace('http://', '').replace('https://', '').split('/')[0]
        def is_secure(self):
            return base_url.startswith('https://')

    routes = [
        ('/', 'Home Page', 'Core'),
        ('/projects/', 'Projects Showcase', 'Catalog'),
        ('/tools/', 'AI Tools Directory', 'Directory'),
        ('/workshop/', '3-Day AI Bootcamp', 'Education'),
        ('/case-studies/', 'Client Case Studies', 'Showcase'),
        ('/ai-roadmap/', 'AI Career Roadmap', 'Guide'),
        ('/blog/', 'Blog & Resource Center', 'Blog'),
        ('/privacy/', 'Privacy Policy', 'Legal'),
        ('/terms/', 'Terms of Service', 'Legal'),
        ('/refund/', 'Refund Policy', 'Legal'),
    ]

    results = []
    for path, name, category in routes:
        req = MockRequest(path)
        seo = get_seo_for_request(req)
        title_len = len(seo['meta_title'])
        desc_len = len(seo['meta_description'])
        
        results.append({
            'path': path,
            'name': name,
            'category': category,
            'is_indexable': seo['is_indexable'],
            'robots': seo['robots'],
            'meta_title': seo['meta_title'],
            'title_len': title_len,
            'title_status': 'good' if 30 <= title_len <= 70 else 'warning',
            'meta_description': seo['meta_description'],
            'desc_len': desc_len,
            'desc_status': 'good' if 100 <= desc_len <= 165 else 'warning',
            'canonical_url': seo['canonical_url'],
            'schema_types': seo['schema_types'],
            'has_og_image': bool(seo['og_image']),
        })

    return results


def auto_generate_all_seo_data(request=None):
    """
    Populates or synchronizes SEOData database records with the automated best-practice values.
    """
    statuses = get_all_site_routes_seo_status(request)
    created_or_updated = 0
    for s in statuses:
        obj, _ = SEOData.objects.update_or_create(
            path=s['path'],
            defaults={
                'meta_title': s['meta_title'],
                'meta_description': s['meta_description'],
                'canonical_url': s['canonical_url'],
                'og_title': s['meta_title'],
                'og_description': s['meta_description'],
                'robots': s['robots'],
                'is_indexable': s['is_indexable'],
                'schema_type': ", ".join(s['schema_types']) if s['schema_types'] else "Auto",
            }
        )
        created_or_updated += 1
    return created_or_updated
