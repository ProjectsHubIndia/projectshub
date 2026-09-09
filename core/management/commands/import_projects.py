import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import (
    SiteSettings, NavigationItem, SocialLink, StatItem,
    ProjectCategory, Technology, Project,
    ToolCategory, AITool,
    Service, ServiceFeature,
    CaseStudy, CaseStudyMetric,
    Testimonial, FAQCategory, FAQ,
    BlogCategory, Tag, BlogPost,
    Redirect
)


class Command(BaseCommand):
    help = 'Import and sync all ProjectsHub entities (Projects, Tools, Services, Case Studies, Testimonials, FAQs, SiteSettings)'

    def handle(self, *args, **options):
        self.stdout.write('Initializing ProjectsHub Data Import & Sync...')
        self.sync_site_settings()
        self.sync_social_links()
        self.sync_stats()
        self.sync_categories_and_technologies()
        self.sync_projects()
        self.sync_tools()
        self.sync_services()
        self.sync_case_studies()
        self.sync_testimonials()
        self.sync_faqs()
        self.sync_navigation()
        self.sync_redirects()
        self.stdout.write(self.style.SUCCESS('[OK] Successfully imported and synchronized all ProjectsHub database content!'))

    def sync_site_settings(self):
        settings = SiteSettings.get_settings()
        settings.site_name = 'ProjectsHub'
        settings.tagline = 'From Ideas to AI-Powered Products'
        settings.primary_email = 'support@projectshub.co.in'
        settings.phone = '+91 9213472954'
        settings.whatsapp_number = '919213472954'
        settings.location = 'Gujarat, India (Remote-Friendly)'
        settings.response_time = 'Within 24 hours'
        settings.hero_headline_prefix = 'Real-World AI Projects &'
        settings.hero_headline_highlight = 'Free Tools'
        settings.hero_subtitle = (
            'Real-world AI and machine learning projects with source code and mentorship '
            'for students, plus custom AI development and automation for businesses.'
        )
        settings.save()
        self.stdout.write('  [OK] SiteSettings configured')

    def sync_social_links(self):
        links = [
            ('github', 'GitHub', 'https://github.com/ProjectsHub', 1),
            ('linkedin', 'LinkedIn', 'https://linkedin.com/company/projectshub', 2),
            ('whatsapp', 'WhatsApp', 'https://wa.me/919213472954?text=Hi%20ProjectsHub%2C%20I%20want%20to%20book%20a%20free%20consultation.', 3),
            ('instagram', 'Instagram', 'https://instagram.com/projectshub.ai', 4),
            ('email', 'Email Support', 'mailto:support@projectshub.co.in', 5),
        ]
        for platform, label, url, order in links:
            SocialLink.objects.update_or_create(
                platform=platform,
                defaults={'label': label, 'url': url, 'order': order, 'is_active': True}
            )
        self.stdout.write('  [OK] SocialLinks synchronized')

    def sync_stats(self):
        stats = [
            # Hero stats
            ('hero', 'AI Projects', '50+', 'Curated production-ready machine learning projects', 'blue', 1),
            ('hero', 'Free Tools', '10+', 'Instant developer & student utilities with zero signup', 'purple', 2),
            ('hero', 'Happy Users', '500+', 'Students & businesses using our tools daily', 'green', 3),

            # Numbers section stats
            ('numbers', 'Free AI Tools', '10+', 'Resume builder, image tools, text utilities & more', 'blue', 1),
            ('numbers', 'Projects Showcased', '50+', 'Machine Learning, Django, APIs & Data Science', 'purple', 2),
            ('numbers', 'Happy Users', '500+', 'Active students, developers & business teams', 'green', 3),
            ('numbers', 'Support Response', '< 24h', 'Guaranteed expert response to all inquiries', 'orange', 4),

            # Trust / Experience
            ('about', 'Projects Delivered', '150+', 'Custom AI and software deliveries across India', 'purple', 1),
            ('about', 'Years Experience', '8+', 'Deep engineering expertise in ML and cloud', 'blue', 2),
        ]
        for section, label, val, desc, icon, order in stats:
            StatItem.objects.update_or_create(
                section=section, label=label,
                defaults={'value': val, 'description': desc, 'icon': icon, 'order': order, 'is_active': True}
            )
        self.stdout.write('  [OK] StatItems synchronized')

    def sync_categories_and_technologies(self):
        cats = [
            ('Machine Learning', 'ml', '🧠', 'Deep learning, neural networks, predictive models, and classical ML algorithms.', 1),
            ('Django & Backend', 'backend', '⚡', 'Scalable REST APIs, ASGI websockets, microservices, and backend pipelines.', 2),
            ('Data Science', 'data', '📊', 'Data analytics, automated dashboards, feature engineering, and big data ETL.', 3),
            ('Cloud & DevOps', 'cloud', '☁️', 'Dockerized microservices, Kubernetes clusters, and automated AWS/GCP pipelines.', 4),
            ('NLP & LLMs', 'nlp', '💬', 'Retrieval-Augmented Generation (RAG), vector embeddings, and LLM fine-tuning.', 5),
            ('Full Stack AI', 'full-stack', '🚀', 'End-to-end applications combining modern frontend with intelligent AI inference.', 6),
        ]
        for name, slug, icon, desc, order in cats:
            ProjectCategory.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'description': desc, 'order': order}
            )

        techs = [
            ('Python', 'python', 'python', 'https://python.org', 1),
            ('Django', 'django', 'django', 'https://djangoproject.com', 2),
            ('FastAPI', 'fastapi', 'fastapi', 'https://fastapi.tiangolo.com', 3),
            ('React', 'react', 'react', 'https://react.dev', 4),
            ('PyTorch', 'pytorch', 'pytorch', 'https://pytorch.org', 5),
            ('TensorFlow', 'tensorflow', 'tensorflow', 'https://tensorflow.org', 6),
            ('PostgreSQL', 'postgresql', 'postgresql', 'https://postgresql.org', 7),
            ('Redis', 'redis', 'redis', 'https://redis.io', 8),
            ('Docker', 'docker', 'docker', 'https://docker.com', 9),
            ('Kubernetes', 'kubernetes', 'kubernetes', 'https://kubernetes.io', 10),
            ('AWS', 'aws', 'amazonaws', 'https://aws.amazon.com', 11),
            ('NLP', 'nlp', 'nlp', 'https://projectshub.co.in', 12),
            ('RAG', 'rag', 'rag', 'https://projectshub.co.in', 13),
            ('BERT', 'bert', 'bert', 'https://huggingface.co', 14),
            ('Scikit-learn', 'scikit-learn', 'scikitlearn', 'https://scikit-learn.org', 15),
            ('Pandas', 'pandas', 'pandas', 'https://pandas.pydata.org', 16),
        ]
        for name, slug, icon, url, order in techs:
            Technology.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'website_url': url, 'order': order}
            )
        self.stdout.write('  [OK] Categories and Technologies synchronized')

    def sync_projects(self):
        # Update existing projects to link slug, category_ref, and technologies
        ml_cat = ProjectCategory.objects.filter(slug='ml').first()
        backend_cat = ProjectCategory.objects.filter(slug='backend').first()
        data_cat = ProjectCategory.objects.filter(slug='data').first()
        cloud_cat = ProjectCategory.objects.filter(slug='cloud').first()

        category_mapping = {
            'ml': ml_cat,
            'backend': backend_cat,
            'data': data_cat,
            'cloud': cloud_cat,
        }

        all_techs = {t.name.lower(): t for t in Technology.objects.all()}

        for project in Project.objects.all():
            if not project.slug:
                project.slug = slugify(project.title) or f"project-{project.id}"
            
            if project.category in category_mapping:
                project.category_ref = category_mapping[project.category]

            if not project.meta_title:
                project.meta_title = f"{project.title} | AI ProjectsHub"
            if not project.meta_description:
                project.meta_description = project.description[:155] if project.description else ''

            project.is_published = project.is_active
            project.save()

            # Link technologies from tags string
            if project.tags:
                tag_parts = [t.strip().lower() for t in project.tags.split(',') if t.strip()]
                for tag in tag_parts:
                    for tech_name, tech_obj in all_techs.items():
                        if tech_name in tag:
                            project.technologies.add(tech_obj)

        self.stdout.write(f'  [OK] Updated {Project.objects.count()} projects with slugs, categories, and technologies')

    def sync_tools(self):
        tool_cats = [
            ('Writing & Text', 'text', 1),
            ('Developer & Code', 'dev', 2),
            ('Chatbots & LLMs', 'chat', 3),
            ('Career & Interview', 'career', 4),
            ('SEO & Growth', 'seo', 5),
            ('Utilities', 'utils', 6),
        ]
        tool_cat_objs = {}
        for name, slug, order in tool_cats:
            cat, _ = ToolCategory.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'order': order}
            )
            tool_cat_objs[slug] = cat

        tools_data = [
            {
                'name': 'AI Text Generator',
                'slug': 'ai-text-generator',
                'description': 'Generate high-quality blog posts, product descriptions, emails, and documentation in seconds using GPT-powered models.',
                'cat_slug': 'text',
                'icon': '🤖',
                'gradient': 'linear-gradient(135deg, #1e40af, #3b82f6)',
                'url': 'https://tools.projectshub.co.in/',
                'order': 1,
            },
            {
                'name': 'Code Explainer',
                'slug': 'code-explainer',
                'description': 'Paste any code snippet in Python, JavaScript, SQL, or C++ and get a step-by-step plain-English explanation with optimization tips.',
                'cat_slug': 'dev',
                'icon': '🧠',
                'gradient': 'linear-gradient(135deg, #1e3a5f, #6366f1)',
                'url': 'https://tools.projectshub.co.in/',
                'order': 2,
            },
            {
                'name': 'AI Chatbot Builder',
                'slug': 'ai-chatbot-builder',
                'description': 'Design custom AI conversational assistants for websites in minutes without coding. Configure knowledge base and tone effortlessly.',
                'cat_slug': 'chat',
                'icon': '💬',
                'gradient': 'linear-gradient(135deg, #065f46, #10b981)',
                'url': 'https://tools.projectshub.co.in/',
                'order': 3,
            },
            {
                'name': 'Interview Prep AI',
                'slug': 'interview-prep-ai',
                'description': 'Enter your target role and get 20 tailored technical + behavioral interview questions complete with ideal STAR answer frameworks.',
                'cat_slug': 'career',
                'icon': '🎙️',
                'gradient': 'linear-gradient(135deg, #881337, #f43f5e)',
                'url': 'https://tools.projectshub.co.in/',
                'order': 4,
            },
            {
                'name': 'SEO Keyword Analyzer',
                'slug': 'seo-keyword-analyzer',
                'description': 'Analyze content for SEO ranking strength. Check keyword density, readability scores, search intent, and structural suggestions.',
                'cat_slug': 'seo',
                'icon': '🔍',
                'gradient': 'linear-gradient(135deg, #4c1d95, #7c3aed)',
                'url': 'https://tools.projectshub.co.in/',
                'order': 5,
            },
            {
                'name': 'Cold Email Writer',
                'slug': 'cold-email-writer',
                'description': 'Write hyper-personalized cold outreach emails for job hunting, client acquisition, or investor pitches with proven response rates.',
                'cat_slug': 'text',
                'icon': '✉️',
                'gradient': 'linear-gradient(135deg, #134e4a, #14b8a6)',
                'url': 'https://tools.projectshub.co.in/',
                'order': 6,
            },
            {
                'name': 'Free Resume Builder',
                'slug': 'free-resume-builder',
                'description': 'Create ATS-friendly software engineering and AI resumes with pre-built bullet point suggestions and one-click PDF export.',
                'cat_slug': 'career',
                'icon': '📄',
                'gradient': 'linear-gradient(135deg, #312e81, #4f46e5)',
                'url': 'https://tools.projectshub.co.in/',
                'order': 7,
            },
            {
                'name': 'PDF Utilities & Converters',
                'slug': 'pdf-utilities',
                'description': 'Split, merge, compress, and extract text and tables from PDF documents completely client-side with no uploads stored.',
                'cat_slug': 'utils',
                'icon': '📑',
                'gradient': 'linear-gradient(135deg, #7c2d12, #ea580c)',
                'url': 'https://tools.projectshub.co.in/',
                'order': 8,
            },
            {
                'name': 'Image to Text & OCR',
                'slug': 'image-to-text-ocr',
                'description': 'Extract printed or handwritten text from screenshots, scanned notes, and charts with deep OCR precision.',
                'cat_slug': 'utils',
                'icon': '🖼️',
                'gradient': 'linear-gradient(135deg, #164e63, #06b6d4)',
                'url': 'https://tools.projectshub.co.in/',
                'order': 9,
            },
        ]

        for td in tools_data:
            AITool.objects.update_or_create(
                slug=td['slug'],
                defaults={
                    'name': td['name'],
                    'description': td['description'],
                    'category': tool_cat_objs.get(td['cat_slug']),
                    'category_slug': td['cat_slug'],
                    'icon': td['icon'],
                    'icon_bg_gradient': td['gradient'],
                    'external_url': td['url'],
                    'is_free': True,
                    'featured': True,
                    'is_published': True,
                    'sort_order': td['order'],
                }
            )
        self.stdout.write(f'  [OK] Synchronized {len(tools_data)} Free AI Tools')

    def sync_services(self):
        services_data = [
            {
                'title': 'AI Development',
                'slug': 'ai-development',
                'target': 'business',
                'short_desc': 'Custom AI applications, proprietary fine-tuned LLMs, and intelligent automation built for production scale.',
                'icon': 'cpu',
                'order': 1,
                'features': [
                    'Custom LLM Fine-Tuning & Prompt Engineering',
                    'Retrieval-Augmented Generation (RAG) Architecture',
                    'Computer Vision & Object Detection Pipelines',
                    'Autonomous AI Agents & Tool Calling',
                ]
            },
            {
                'title': 'AI Automation',
                'slug': 'ai-automation',
                'target': 'business',
                'short_desc': 'Eliminate repetitive workflows and human bottlenecks with autonomous AI background pipelines.',
                'icon': 'zap',
                'order': 2,
                'features': [
                    'Intelligent Document & Invoice Processing',
                    'Customer Support Ticket Auto-Resolution',
                    'CRM & Database Automated Syncing',
                    '24/7 Background Data Ingestion & Alerts',
                ]
            },
            {
                'title': 'AI Integration & Services',
                'slug': 'ai-integration',
                'target': 'business',
                'short_desc': 'Seamlessly connect OpenAI, Anthropic, Gemini, or local open-source models into your existing stack.',
                'icon': 'layers',
                'order': 3,
                'features': [
                    'Secure Enterprise API Gateway Setup',
                    'PostgreSQL Vector Search & Embeddings Setup',
                    'Latency & Cost Optimization Architecture',
                    'Full SOC-2 & HIPAA Compliant Data Flow',
                ]
            },
            {
                'title': 'Hands-on Capstone Projects',
                'slug': 'capstone-projects',
                'target': 'student',
                'short_desc': 'Production-ready AI/ML projects with full source code, architecture diagrams, and complete documentation for final year submissions.',
                'icon': 'folder',
                'order': 4,
                'features': [
                    'Complete Clean Python/Django/FastAPI Source Code',
                    'Step-by-step Setup & Execution Guide',
                    'System Architecture Diagrams & Flowcharts',
                    'Final Year Project Report & Presentation Slides',
                ]
            },
            {
                'title': '1-on-1 Mentorship Sessions',
                'slug': '1-on-1-mentorship',
                'target': 'student',
                'short_desc': 'Direct private code review, project debugging, and concept clarity with experienced AI engineers.',
                'icon': 'users',
                'order': 5,
                'features': [
                    'Live Screen-sharing Debugging Sessions',
                    'Code Architecture & Performance Optimization',
                    'Viva Voce & Technical Defense Prep',
                    'Personalized Learning Track & Code Best Practices',
                ]
            },
            {
                'title': 'Live Coding Workshops',
                'slug': 'live-coding-workshops',
                'target': 'student',
                'short_desc': 'Intensive multi-day bootcamps building AI systems from zero to live deployment on cloud.',
                'icon': 'video',
                'order': 6,
                'features': [
                    'Live Project Build with Industry Mentors',
                    'Q&A and Hands-on Coding Assignments',
                    'Certificate of Completion for Resumes',
                    'Lifetime Access to Code Repos & Recordings',
                ]
            },
            {
                'title': 'AI Road Map',
                'slug': 'ai-roadmap',
                'target': 'student',
                'short_desc': 'Curated step-by-step career pathway from Python fundamentals to MLOps and LLM engineering.',
                'icon': 'map',
                'order': 7,
                'features': [
                    'Structured Beginner-to-Advanced Milestones',
                    'Curated Free Tools & Open-Source Repositories',
                    'Portfolio Project Recommendations',
                    'Interview Preparation Benchmarks',
                ]
            },
            {
                'title': 'Career Support & Review',
                'slug': 'career-support',
                'target': 'student',
                'short_desc': 'ATS-friendly resume audits, GitHub profile optimizations, and mock interview guidance.',
                'icon': 'award',
                'order': 8,
                'features': [
                    'In-depth Resume Review with Specific Action Items',
                    'GitHub Portfolio Cleanup & README Polish',
                    'Mock Technical & Behavioral Interviews',
                    'Referral Network & Industry Insights',
                ]
            },
        ]

        for s_data in services_data:
            svc, _ = Service.objects.update_or_create(
                slug=s_data['slug'],
                defaults={
                    'title': s_data['title'],
                    'target_audience': s_data['target'],
                    'short_description': s_data['short_desc'],
                    'icon': s_data['icon'],
                    'sort_order': s_data['order'],
                    'is_published': True,
                    'meta_title': f"{s_data['title']} | ProjectsHub",
                    'meta_description': s_data['short_desc'][:155],
                }
            )
            for idx, feat_text in enumerate(s_data['features'], 1):
                ServiceFeature.objects.update_or_create(
                    service=svc,
                    title=feat_text,
                    defaults={'order': idx}
                )
        self.stdout.write(f'  [OK] Synchronized {len(services_data)} Services & Features')

    def sync_case_studies(self):
        case_studies_data = [
            {
                'title': 'AI Document Summarizer for Law Firms — From Zero to MVP in 3 Weeks',
                'slug': 'ai-document-summarizer-law-firms',
                'client': 'LexAI — Startup',
                'industry': 'LegalTech',
                'emoji': '⚖️',
                'gradient': 'linear-gradient(135deg, #1e3a5f, #3b82f6)',
                'summary': 'A law firm startup needed an AI-powered document summarizer before an investor demo. We designed, built, and deployed a full Django + GPT-4 SaaS product in 21 days — helping them close a seed round.',
                'timeline': '3 Weeks',
                'order': 1,
                'metrics': [
                    ('MVP Delivery', '3 Weeks', 'Zero to production deployment'),
                    ('Beta Users', '100+', 'Active legal professionals'),
                    ('Seed Round', 'Closed', 'Funded post-demo'),
                ]
            },
            {
                'title': 'AI-Powered Product Recommendation Engine that Boosted Revenue by 38%',
                'slug': 'ai-product-recommendation-engine',
                'client': 'ShopSmart — D2C Brand',
                'industry': 'E-Commerce',
                'emoji': '🛒',
                'gradient': 'linear-gradient(135deg, #064e3b, #10b981)',
                'summary': 'A D2C fashion brand was losing customers due to irrelevant product suggestions. We built a collaborative filtering recommendation engine integrated into their existing Shopify store.',
                'timeline': '6 Weeks',
                'order': 2,
                'metrics': [
                    ('Revenue', '+38%', 'Quarter-over-quarter growth'),
                    ('Click-Through', '+62%', 'On recommended products'),
                    ('To Ship', '6 Weeks', 'End-to-end delivery'),
                ]
            },
            {
                'title': 'Personalized Learning Assistant that Reduced Student Drop-off by 45%',
                'slug': 'personalized-learning-assistant-edtech',
                'client': 'EduPath — EdTech Platform',
                'industry': 'EdTech',
                'emoji': '🎓',
                'gradient': 'linear-gradient(135deg, #4c1d95, #7c3aed)',
                'summary': "An online learning platform was losing students mid-course. We built an AI tutor that adapts to each student's pace, detects confusion, and sends personalized nudges — dramatically improving completion rates.",
                'timeline': '8 Weeks',
                'order': 3,
                'metrics': [
                    ('Drop-off', '-45%', 'Reduced student churn'),
                    ('Completion', '+3x', 'Course finish rates'),
                    ('To Launch', '8 Weeks', 'Complete rollout'),
                ]
            },
            {
                'title': 'Automated Patient Report Analyzer Saving 4 Hours Per Day Per Doctor',
                'slug': 'automated-patient-report-analyzer',
                'client': 'MedTrack — HealthTech',
                'industry': 'Healthcare',
                'emoji': '🏥',
                'gradient': 'linear-gradient(135deg, #7c2d12, #f97316)',
                'summary': 'Doctors were spending hours manually reading lab reports. We built a FastAPI + OpenAI system that extracts key values, flags anomalies, and generates plain-language summaries instantly.',
                'timeline': '5 Weeks',
                'order': 4,
                'metrics': [
                    ('Saved/Day', '4 hrs', 'Per physician on charts'),
                    ('Accuracy', '98%', 'Verified clinical extraction'),
                    ('To Deploy', '5 Weeks', 'Pilot rollout in hospital'),
                ]
            },
            {
                'title': 'Natural Language Analytics Dashboard — Ask Your Data a Question',
                'slug': 'natural-language-analytics-dashboard',
                'client': 'DataPulse — Analytics SaaS',
                'industry': 'SaaS',
                'emoji': '📊',
                'gradient': 'linear-gradient(135deg, #1e1b4b, #6366f1)',
                'summary': 'A SaaS analytics company wanted users to query their dashboards in plain English. We built an NLP-to-SQL engine that lets non-technical users ask business questions and get instant chart answers.',
                'timeline': '10 Weeks',
                'order': 5,
                'metrics': [
                    ('User Retention', '+210%', 'Increase in daily usage'),
                    ('SQL Knowledge', '0 SQL', 'Natural language interface'),
                    ('To Launch', '10 Weeks', 'Full SaaS integration'),
                ]
            },
            {
                'title': 'AI Route Optimizer that Cut Delivery Costs by 27% in 60 Days',
                'slug': 'ai-route-optimizer-logistics',
                'client': 'SwiftMove — Logistics Startup',
                'industry': 'Logistics',
                'emoji': '🚚',
                'gradient': 'linear-gradient(135deg, #0c4a6e, #0ea5e9)',
                'featured_image': 'case_studies/swiftmove_route_optimizer.jpg',
                'summary': 'A last-mile delivery startup was burning money on inefficient routes. We built a machine learning route optimizer that factors in traffic, weather, and delivery windows — cutting costs significantly.',
                'timeline': '60 Days',
                'order': 6,
                'metrics': [
                    ('Delivery Cost', '-27%', 'Reduction in fuel & labor'),
                    ('On-Time Rate', '+19%', 'SLA compliance improved'),
                    ('To Results', '60 Days', 'Measured ROI timeframe'),
                ]
            },
        ]

        img_map = {
            'ai-document-summarizer-law-firms': 'case_studies/lexai_doc_summarizer.jpg',
            'ai-product-recommendation-engine': 'case_studies/shopsmart_recommendation.jpg',
            'personalized-learning-assistant-edtech': 'case_studies/edupath_learning_assistant.jpg',
            'automated-patient-report-analyzer': 'case_studies/medtrack_patient_report.jpg',
            'natural-language-analytics-dashboard': 'case_studies/datapulse_nlp_analytics.jpg',
            'ai-route-optimizer-logistics': 'case_studies/swiftmove_route_optimizer.jpg',
        }

        for cs_data in case_studies_data:
            cs, _ = CaseStudy.objects.update_or_create(
                slug=cs_data['slug'],
                defaults={
                    'title': cs_data['title'],
                    'client': cs_data['client'],
                    'industry': cs_data['industry'],
                    'icon_emoji': cs_data['emoji'],
                    'band_gradient': cs_data['gradient'],
                    'featured_image': cs_data.get('featured_image', img_map.get(cs_data['slug'], '')),
                    'summary': cs_data['summary'],
                    'timeline': cs_data['timeline'],
                    'is_featured': True,
                    'is_published': True,
                    'sort_order': cs_data['order'],
                }
            )
            for idx, (label, val, desc) in enumerate(cs_data['metrics'], 1):
                CaseStudyMetric.objects.update_or_create(
                    case_study=cs,
                    label=label,
                    defaults={'value': val, 'description': desc, 'order': idx}
                )
        self.stdout.write(f'  [OK] Synchronized {len(case_studies_data)} Case Studies & Metrics')

    def sync_testimonials(self):
        testimonials_data = [
            ('Sarah J.', 'CS Student', 'Stanford University', 'purple', 5,
             "ProjectsHub's free AI tools are incredible. The resume builder helped me land my first software engineering internship within weeks!", 1),
            ('David M.', 'Data Scientist', 'FinTech Corp', 'cyan', 5,
             "The production-ready Machine Learning projects gave me exactly what I needed to understand real-world model deployment.", 2),
            ('Elena R.', 'Startup Founder', 'HealthTech Innovations', 'orange', 5,
             "We requested a custom internal tool for our startup and they delivered a flawless, scalable Django backend in record time.", 3),
            ('Michael T.', 'UX Designer', 'Creative Tech Labs', 'purple', 5,
             "The UI/UX is unmatched. Using the image generation and text tools on this platform feels so much better than any premium tool I've used.", 4),
            ('James K.', 'Backend Dev', 'Logistics Co', 'blue', 5,
             "The free API integrations they showcase are incredibly well-documented. Saved me countless hours of debugging.", 5),
            ('Anita P.', 'Machine Learning Eng', 'Enterprise AI', 'green', 5,
             "Support is lightning fast. I had a question about one of the data science repos and got a detailed reply the same day.", 6),
        ]
        for name, role, comp, color, rating, content, order in testimonials_data:
            Testimonial.objects.update_or_create(
                name=name,
                defaults={
                    'role': role,
                    'company': comp,
                    'avatar_color': color,
                    'rating': rating,
                    'content': content,
                    'is_featured': True,
                    'is_published': True,
                    'sort_order': order,
                }
            )
        self.stdout.write(f'  [OK] Synchronized {len(testimonials_data)} Testimonials')

    def sync_faqs(self):
        cat, _ = FAQCategory.objects.get_or_create(name='General', defaults={'slug': 'general', 'order': 1})
        faqs_data = [
            ("Are the AI tools completely free to use?",
             "Yes! All our free AI tools — including the resume builder, PDF tools, image tools, and text utilities — are completely free to use, with no signup required. We believe in providing accessible AI tools for students and businesses.", 1),
            ("What kind of AI projects are showcased on ProjectsHub?",
             "We showcase production-ready AI and machine learning projects with source code — including Machine Learning models, Django and FastAPI backends, Data Science analytics, NLP, RAG, and full-stack applications for students and businesses.", 2),
            ("Can I request custom AI development for my business?",
             "Absolutely. We provide custom AI development and automation tailored to your needs — whether you are a student, a startup, or a growing business in India. Use the contact form below to get in touch!", 3),
            ("Do I need to create an account to use the tools?",
             "No account is required to use our free AI tools. You can jump right in and start building resumes, converting PDFs, or editing images instantly — no signup needed.", 4),
            ("How fast is your support response time?",
             "We take pride in our rapid support. If you reach out to us with a question or project inquiry, you will typically receive a personalized response in under 24 hours.", 5),
            ("Are the AI and ML projects suitable for beginners and final-year students?",
             "Yes! Our AI and machine learning projects are designed to be highly educational, with clean code and full documentation — ideal for final-year projects and beginners of all skill levels.", 6),
        ]
        for q, a, order in faqs_data:
            FAQ.objects.update_or_create(
                question=q,
                defaults={
                    'category': cat,
                    'answer': a,
                    'sort_order': order,
                    'is_published': True,
                }
            )
        self.stdout.write(f'  [OK] Synchronized {len(faqs_data)} FAQs')

    def sync_navigation(self):
        nav_items = [
            ('Our Work', '/projects/', 'main', 1),
            ('Who We Help', '/#about', 'main', 2),
            ('How We Help', '#how-we-help', 'main', 3),
            ('Why Projects Hub', '/#why-projectshub', 'main', 4),
            ('Blog', '/blog/', 'main', 5),
            ('Contact Us', '/#contact', 'main', 6),

            # Mega menu items
            ('Our Projects', '/projects/', 'our_work', 1),
            ('AI Case Studies', '/case-studies/', 'our_work', 2),
            ('Free AI Tools', 'https://tools.projectshub.co.in/', 'our_work', 3),

            ('1-on-1 Mentorship', '/workshop/', 'how_we_help_students', 1),
            ('Hands-on Capstone Projects', '/projects/', 'how_we_help_students', 2),
            ('Live Coding Workshops', '/workshop/', 'how_we_help_students', 3),
            ('AI Road Map', '/ai-roadmap/', 'how_we_help_students', 4),

            ('AI Development', '/services/ai-development/', 'how_we_help_business', 1),
            ('AI Automation', '/services/ai-automation/', 'how_we_help_business', 2),
            ('AI Integration & Services', '/services/ai-integration/', 'how_we_help_business', 3),
            ('Industries', '/industries/', 'how_we_help_business', 4),
        ]
        for title, url, group, order in nav_items:
            NavigationItem.objects.update_or_create(
                title=title, group=group,
                defaults={'url': url, 'order': order, 'is_active': True}
            )
        self.stdout.write('  [OK] NavigationItems synchronized')

    def sync_redirects(self):
        redirects_data = [
            ('/portfolio/', '/projects/', 301, 'Legacy portfolio link'),
            ('/ai-tools/', '/tools/', 301, 'Legacy tools link'),
            ('/services/', '/services/ai-development/', 301, 'General services redirect'),
            ('/workshop-day1/', '/workshop/', 301, 'Legacy day 1 workshop redirect'),
        ]
        for old, new, code, notes in redirects_data:
            Redirect.objects.update_or_create(
                old_path=old,
                defaults={'new_path': new, 'status_code': code, 'is_active': True, 'notes': notes}
            )
        self.stdout.write('  [OK] URL Redirects synchronized')
