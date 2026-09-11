import re
from urllib.parse import parse_qs, urlparse
from django.db import models
from django.utils.text import slugify


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CORE & SITE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class SiteSettings(models.Model):
    """Global configuration for ProjectsHub managed in Django admin."""
    site_name = models.CharField(max_length=100, default='ProjectsHub')
    tagline = models.CharField(max_length=255, default='From Ideas to AI-Powered Products')
    primary_email = models.EmailField(default='support@projectshub.co.in')
    phone = models.CharField(max_length=50, default='+91 9213472954')
    whatsapp_number = models.CharField(max_length=50, default='919213472954')
    location = models.CharField(max_length=200, default='Gujarat, India (Remote-Friendly)')
    response_time = models.CharField(max_length=100, default='Within 24 hours')
    
    # Visual branding
    hero_headline_prefix = models.CharField(max_length=200, default='Real-World AI Projects &')
    hero_headline_highlight = models.CharField(max_length=100, default='Free Tools')
    hero_subtitle = models.TextField(
        default='Real-world AI and machine learning projects with source code and mentorship for students, plus custom AI development and automation for businesses.'
    )
    logo_dark = models.ImageField(upload_to='branding/', blank=True, null=True)
    logo_light = models.ImageField(upload_to='branding/', blank=True, null=True)

    # Mega Menu "Our Work" Footer Bar
    mega_popular_label = models.CharField(
        max_length=60, default='Popular:', blank=True,
        help_text="Label preceding bottom tags in 'Our Work' mega menu (e.g. 'Popular:' or 'Trending:')"
    )
    mega_browse_all_text = models.CharField(
        max_length=80, default='Browse All Projects →', blank=True,
        help_text="CTA text in 'Our Work' mega menu footer"
    )
    mega_browse_all_url = models.CharField(
        max_length=255, default='/projects/', blank=True,
        help_text="CTA link destination in 'Our Work' mega menu footer"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return f"{self.site_name} Settings"

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


class NavigationItem(models.Model):
    """Dynamic navigation link or mega-menu section with full UI/UX control."""
    GROUP_CHOICES = [
        ('main', 'Primary Top Navigation'),
        ('our_work', 'Mega Menu — Our Work (Cards)'),
        ('popular_tags', 'Mega Menu — Popular Tags (Bottom Pills)'),
        ('who_we_help', 'Section Link — Who We Help'),
        ('how_we_help_students', 'Mega Menu — How We Help (Students)'),
        ('how_we_help_business', 'Mega Menu — How We Help (Businesses)'),
        ('footer_work', 'Footer — Our Work'),
        ('footer_students', 'Footer — Students'),
        ('footer_business', 'Footer — Businesses'),
        ('footer_legal', 'Footer — Legal'),
    ]

    BADGE_COLOR_CHOICES = [
        ('cyan', 'Cyan / Sky Blue'),
        ('emerald', 'Emerald / Green'),
        ('purple', 'Purple / Indigo'),
        ('amber', 'Amber / Yellow'),
        ('rose', 'Rose / Red'),
        ('blue', 'Classic Blue'),
    ]

    title = models.CharField(max_length=120)
    url = models.CharField(max_length=255, help_text="Relative (e.g. /projects/) or absolute URL")
    group = models.CharField(max_length=40, choices=GROUP_CHOICES, default='main')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_items')
    description = models.CharField(max_length=255, blank=True, help_text="Short subtitle or card description")
    badge_text = models.CharField(max_length=40, blank=True, help_text="Optional badge e.g. '50+ Projects', 'HOT', 'NEW'")
    badge_color = models.CharField(max_length=30, blank=True, default='cyan', choices=BADGE_COLOR_CHOICES, help_text="Badge color styling")
    image = models.ImageField(upload_to='navigation/', blank=True, null=True, help_text="Card banner or thumbnail image")
    icon_svg = models.TextField(blank=True, help_text="Emoji or inline SVG icon")
    open_in_new_tab = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Navigation Item'
        verbose_name_plural = 'Navigation Items'

    def __str__(self):
        badge = f" [{self.badge_text}]" if self.badge_text else ""
        return f"[{self.get_group_display()}] {self.title}{badge} -> {self.url}"


class MegaMenuTag(NavigationItem):
    """
    Proxy model to manage 'Popular Tags' pills shown in the Our Work Mega Menu footer.
    Allows administrators to easily add, reorder, and activate/deactivate bottom pills.
    """
    class Meta:
        proxy = True
        verbose_name = 'Popular Tag (Mega Menu)'
        verbose_name_plural = 'Popular Tags (Mega Menu)'


class SocialLink(models.Model):
    """Social media links shown across header and footer."""
    PLATFORM_CHOICES = [
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('whatsapp', 'WhatsApp'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('twitter', 'X / Twitter'),
        ('email', 'Email'),
    ]

    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES)
    label = models.CharField(max_length=60, blank=True)
    url = models.URLField()
    icon_svg = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Social Link'
        verbose_name_plural = 'Social Links'

    def __str__(self):
        return f"{self.get_platform_display()} ({self.url})"


class StatItem(models.Model):
    """Unified stats for Hero, Numbers section, and trust badges."""
    SECTION_CHOICES = [
        ('hero', 'Hero Trust Bar'),
        ('numbers', 'ProjectsHub in Numbers'),
        ('about', 'About / Trust Section'),
    ]

    section = models.CharField(max_length=30, choices=SECTION_CHOICES, default='numbers')
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50, help_text="e.g. 50+, 10+, < 24h, 500+")
    description = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=50, blank=True, default='star', help_text="Icon identifier e.g. blue, purple, green, orange")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Stat Item'
        verbose_name_plural = 'Stat Items'

    def __str__(self):
        return f"{self.label}: {self.value} ({self.section})"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PROJECTS & TECHNOLOGIES
# ═══════════════════════════════════════════════════════════════════════════════

class ProjectCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji or icon code")
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Project Category'
        verbose_name_plural = 'Project Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Technology(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=150, blank=True, help_text="SimpleIcon slug or SVG symbol e.g. python, fastapi, pytorch")
    website_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Technology'
        verbose_name_plural = 'Technologies'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(models.Model):
    CATEGORY_CHOICES = [
        ('ml', 'Machine Learning'),
        ('backend', 'Backend'),
        ('data', 'Data'),
        ('cloud', 'Cloud'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True, help_text="URL slug e.g. ai-sentiment-analyser")
    description = models.TextField()
    detailed_description = models.TextField(
        blank=True,
        help_text="Detailed description for the project detail page"
    )
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default='ml'
    )
    category_ref = models.ForeignKey(
        ProjectCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects'
    )
    technologies = models.ManyToManyField(
        Technology, blank=True, related_name='projects'
    )
    tags = models.CharField(
        max_length=300,
        help_text="Comma-separated tags e.g. PyTorch, FastAPI, AWS"
    )

    # Images
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='projects/thumbnails/', blank=True, null=True)
    image_url = models.URLField(
        blank=True,
        help_text="External image URL (used if no uploaded image)"
    )

    # Links
    project_url = models.URLField(blank=True, help_text="Link to live project or case study")
    github_url = models.URLField(blank=True, help_text="GitHub repository URL")
    demo_url = models.URLField(blank=True, help_text="Interactive live demo link")
    external_url = models.URLField(blank=True, help_text="External portfolio or documentation link")
    youtube_url = models.URLField(blank=True, help_text="YouTube demo URL")
    download_file = models.FileField(
        upload_to='project_files/', blank=True, null=True,
        help_text="Downloadable source code or documentation ZIP"
    )

    # Metadata & Details
    subtitle = models.CharField(max_length=300, blank=True, help_text="Tagline on detail page")
    year = models.CharField(max_length=10, blank=True, default='2025')
    role = models.CharField(max_length=100, blank=True, default='AI/ML Engineer')
    duration = models.CharField(max_length=100, blank=True, default='2-4 Weeks')
    team_size = models.CharField(max_length=100, blank=True, default='Solo Project')
    difficulty = models.CharField(max_length=50, blank=True, default='Intermediate')
    case_study_url = models.URLField(blank=True)

    # Pricing
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0, blank=True)
    price_label = models.CharField(max_length=50, blank=True, default='Free')

    # Visibility & Display Flags
    featured = models.BooleanField(default=False, help_text="Highlight as top featured project")
    show_on_index = models.BooleanField(default=False, help_text="Display in featured section on homepage")
    is_active = models.BooleanField(default=True, help_text="Active / Visible across site")
    is_published = models.BooleanField(default=True, help_text="Publish status")
    order = models.PositiveIntegerField(default=0, help_text="Sort order (lower = first)")

    # SEO metadata
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    canonical_url = models.URLField(blank=True)
    og_title = models.CharField(max_length=255, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.ImageField(upload_to='seo/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or f"project-{self.pk or 'item'}"
            unique_slug = base_slug
            num = 1
            while Project.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        if not self.meta_title:
            self.meta_title = f"{self.title} | AI ProjectsHub"
        if not self.meta_description:
            self.meta_description = self.description[:155] if self.description else ''
        super().save(*args, **kwargs)

    def get_image_src(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return '/static/image/ai-project-ideas-students.webp'

    def get_tags_list(self):
        if self.technologies.exists():
            return [t.name for t in self.technologies.all()]
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_youtube_embed_url(self):
        if not self.youtube_url:
            return ''
        url = self.youtube_url.strip()
        parsed = urlparse(url)
        hostname = parsed.hostname or ''
        path = parsed.path or ''
        if 'youtube.com' in hostname and path == '/watch':
            params = parse_qs(parsed.query)
            video_ids = params.get('v')
            if video_ids:
                return f'https://www.youtube-nocookie.com/embed/{video_ids[0]}?rel=0&modestbranding=1&playsinline=1'
        match = re.match(r'^/([A-Za-z0-9_-]{11})$', path)
        if 'youtu.be' in hostname and match:
            return f'https://www.youtube-nocookie.com/embed/{match.group(1)}?rel=0&modestbranding=1&playsinline=1'
        match = re.match(r'^/(?:embed|v|shorts)/([A-Za-z0-9_-]{11})$', path)
        if 'youtube.com' in hostname and match:
            return f'https://www.youtube-nocookie.com/embed/{match.group(1)}?rel=0&modestbranding=1&playsinline=1'
        return ''


class ProjectImage(models.Model):
    """Gallery & screenshot images for project detail pages."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='detail_images')
    image = models.ImageField(upload_to='projects/detail/')
    caption = models.CharField(max_length=300, blank=True)
    alt = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Project Image'
        verbose_name_plural = 'Project Images'

    def __str__(self):
        return f"{self.project.title} image {self.order}"


class ProjectHighlight(models.Model):
    ICON_CHOICES = [
        ('chart', 'Bar Chart'),
        ('users', 'Users / Team'),
        ('clock', 'Clock / Time'),
        ('star', 'Star / Rating'),
        ('bolt', 'Bolt / Speed'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='highlights')
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='chart')
    value = models.CharField(max_length=100)
    label = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Project Highlight'
        verbose_name_plural = 'Project Highlights'

    def __str__(self):
        return f"{self.project.title} — {self.label}: {self.value}"


class ProjectDiagram(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='diagrams')
    image = models.ImageField(upload_to='projects/diagrams/')
    label = models.CharField(max_length=100, blank=True, default='Architecture')
    title = models.CharField(max_length=200)
    desc = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Project Diagram'
        verbose_name_plural = 'Project Diagrams'

    def __str__(self):
        return f"{self.project.title} — {self.title}"


class ProjectTimelinePhase(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timeline_phases')
    phase = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    desc = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Project Timeline Phase'
        verbose_name_plural = 'Project Timeline Phases'

    def __str__(self):
        return f"{self.project.title} — {self.phase}: {self.title}"


class ProjectFeature(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='price_features')
    text = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Project Feature'
        verbose_name_plural = 'Project Features'

    def __str__(self):
        return f"{self.project.title} — {self.text}"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. FREE AI TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

class ToolCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Tool Category'
        verbose_name_plural = 'Tool Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class AITool(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(ToolCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='tools')
    category_slug = models.CharField(max_length=50, default='all', help_text="e.g. text, dev, chat, career, seo")
    icon = models.CharField(max_length=50, default='🤖', help_text="Emoji or icon code")
    icon_bg_gradient = models.CharField(max_length=100, default='linear-gradient(135deg, #1e40af, #3b82f6)')
    image = models.ImageField(upload_to='tools/', blank=True, null=True)
    external_url = models.URLField(default='https://tools.projectshub.co.in/')
    is_free = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Free AI Tool'
        verbose_name_plural = 'Free AI Tools'

    def __str__(self):
        return self.name

    @property
    def url(self):
        return self.external_url

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. SERVICES
# ═══════════════════════════════════════════════════════════════════════════════

class Service(models.Model):
    AUDIENCE_CHOICES = [
        ('student', 'Students & Beginners'),
        ('business', 'Startups & Businesses'),
        ('both', 'Both Students & Businesses'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    target_audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='both')
    short_description = models.TextField()
    full_description = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to='services/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, default='bolt')
    cta_label = models.CharField(max_length=80, default='Explore Services')
    cta_url = models.CharField(max_length=255, default='/#contact')
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    class Meta:
        ordering = ['sort_order', 'title']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return f"{self.title} ({self.get_target_audience_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ServiceFeature(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Service Feature'
        verbose_name_plural = 'Service Features'

    def __str__(self):
        return f"{self.service.title}: {self.title}"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. CASE STUDIES
# ═══════════════════════════════════════════════════════════════════════════════

class CaseStudy(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    client = models.CharField(max_length=150, help_text="e.g. LexAI — Startup, ShopSmart — D2C Brand")
    industry = models.CharField(max_length=100, help_text="e.g. LegalTech, E-Commerce, EdTech, Healthcare")
    challenge = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    results = models.TextField(blank=True)
    summary = models.TextField(help_text="Overview card summary")
    featured_image = models.ImageField(upload_to='case_studies/', blank=True, null=True)
    icon_emoji = models.CharField(max_length=10, default='📊')
    band_gradient = models.CharField(max_length=100, default='linear-gradient(135deg, #1e3a5f, #3b82f6)')
    timeline = models.CharField(max_length=100, blank=True, default='4-6 Weeks')
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-created_at']
        verbose_name = 'Case Study'
        verbose_name_plural = 'Case Studies'

    def __str__(self):
        return f"{self.title} ({self.client})"

    @property
    def client_name(self):
        return self.client

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class CaseStudyMetric(models.Model):
    case_study = models.ForeignKey(CaseStudy, on_delete=models.CASCADE, related_name='metrics')
    label = models.CharField(max_length=100, help_text="e.g. Revenue, MVP Delivery, Drop-off")
    value = models.CharField(max_length=50, help_text="e.g. +38%, 3 Weeks, -45%")
    description = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Case Study Metric'
        verbose_name_plural = 'Case Study Metrics'

    def __str__(self):
        return f"{self.case_study.title} — {self.label}: {self.value}"


class CaseStudyTechnology(models.Model):
    case_study = models.ForeignKey(CaseStudy, on_delete=models.CASCADE, related_name='technologies')
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Case Study Technology'
        verbose_name_plural = 'Case Study Technologies'


# ═══════════════════════════════════════════════════════════════════════════════
# 6. TESTIMONIALS
# ═══════════════════════════════════════════════════════════════════════════════

class Testimonial(models.Model):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=150, help_text="e.g. CS Student, Data Scientist, Startup Founder")
    company = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    avatar_color = models.CharField(max_length=30, default='purple', help_text="purple, blue, green, cyan, orange")
    rating = models.PositiveSmallIntegerField(default=5)
    content = models.TextField()
    is_featured = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return f"{self.name} ({self.role})"

    @property
    def initial(self):
        return self.name[0].upper() if self.name else 'U'

    @property
    def quote(self):
        return self.content


# ═══════════════════════════════════════════════════════════════════════════════
# 7. FAQS
# ═══════════════════════════════════════════════════════════════════════════════

class FAQCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'FAQ Category'
        verbose_name_plural = 'FAQ Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class FAQ(models.Model):
    category = models.ForeignKey(FAQCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question


# ═══════════════════════════════════════════════════════════════════════════════
# 8. BLOG
# ═══════════════════════════════════════════════════════════════════════════════

class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('ai-tutorials', 'AI Tutorials'),
        ('career', 'Career Advice'),
        ('case-study', 'Case Study'),
        ('engineering', 'Engineering'),
        ('news', 'News'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='ai-tutorials')
    category_ref = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    excerpt = models.TextField()
    lead = models.TextField(blank=True)
    content = models.TextField(blank=True, help_text="Full markdown / HTML content if single-body")

    # Visuals
    emoji = models.CharField(max_length=8, blank=True, default='📝')
    gradient_from = models.CharField(max_length=7, default='#2563eb')
    gradient_to = models.CharField(max_length=7, default='#3b82f6')
    accent = models.CharField(max_length=7, default='#3b82f6')
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    image_url = models.URLField(blank=True)

    # Meta
    read_time = models.CharField(max_length=30, blank=True, default='5 min read')
    published_at = models.DateField()
    author_name = models.CharField(max_length=100, default='Raj Makhijani')
    author_role = models.CharField(max_length=150, blank=True, default='Founder, ProjectsHub')
    author_initials = models.CharField(max_length=4, blank=True, default='RM')

    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-published_at', '-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def __str__(self):
        return self.title

    def get_image_src(self):
        if self.featured_image:
            return self.featured_image.url
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return '/static/image/ai-project-ideas-students.webp'

    def get_lead(self):
        return self.lead or self.excerpt

    def get_gradient(self):
        return f'linear-gradient(135deg, {self.gradient_from}, {self.gradient_to})'


class BlogSection(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='sections')
    heading = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    code = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Blog Section'
        verbose_name_plural = 'Blog Sections'

    def __str__(self):
        return f"{self.post.title} — {self.heading or 'section'}"


# ═══════════════════════════════════════════════════════════════════════════════
# 9. CONTACT & LEADS
# ═══════════════════════════════════════════════════════════════════════════════

class ContactInquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('in_progress', 'In Progress'),
        ('converted', 'Converted'),
        ('closed', 'Closed'),
        ('spam', 'Spam'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=300, default='Project Inquiry')
    message = models.TextField()
    source_page = models.CharField(max_length=255, default='/#contact')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Inquiry'
        verbose_name_plural = 'Contact Inquiries'

    def __str__(self):
        return f"{self.name} ({self.email}) — {self.subject}"


class ContactMessage(models.Model):
    """Retained for backward compatibility with existing data rows."""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Legacy Contact Message'
        verbose_name_plural = 'Legacy Contact Messages'

    def __str__(self):
        return f"{self.full_name} — {self.subject or 'No subject'}"


class ProjectGateLead(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    college_or_org = models.CharField(max_length=300)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project Gate Lead'
        verbose_name_plural = 'Project Gate Leads'

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class IdeaSubmission(models.Model):
    BUDGET_CHOICES = [
        ('under-5k', 'Under ₹5,000'),
        ('5k-20k', '₹5,000 – ₹20,000'),
        ('20k-50k', '₹20,000 – ₹50,000'),
        ('50k-plus', '₹50,000+'),
        ('flexible', 'Flexible / Not sure'),
    ]
    TIMELINE_CHOICES = [
        ('asap', 'ASAP'),
        ('1-month', 'Within 1 month'),
        ('3-months', 'Within 3 months'),
        ('6-months', 'Within 6 months'),
        ('flexible', 'Flexible'),
    ]
    STATUS_CHOICES = [
        ('new', 'New'),
        ('reviewing', 'Reviewing'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    project_title = models.CharField(max_length=300)
    description = models.TextField()
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES, blank=True)
    timeline = models.CharField(max_length=20, choices=TIMELINE_CHOICES, blank=True)
    agreed_to_terms = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Idea Submission'
        verbose_name_plural = 'Idea Submissions'

    def __str__(self):
        return f"{self.full_name} — {self.project_title}"


class WorkshopCard(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    date = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    seats = models.PositiveIntegerField(default=30)
    mode = models.CharField(max_length=100, default="Online (Live)")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_label = models.CharField(max_length=50, blank=True)
    enroll_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Workshop Card'
        verbose_name_plural = 'Workshop Cards'

    def __str__(self):
        return self.title


class WorkshopDay(models.Model):
    workshop = models.ForeignKey(WorkshopCard, on_delete=models.CASCADE, related_name='days')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    date_label = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    topics = models.TextField(blank=True, default='')
    outcome = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['day_number']
        verbose_name = 'Workshop Day'
        verbose_name_plural = 'Workshop Days'

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"


class WorkshopEnrollment(models.Model):
    EXPERIENCE_CHOICES = [
        ('beginner', 'Beginner (No prior experience)'),
        ('basic', 'Basic (Some exposure)'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    REFERRAL_CHOICES = [
        ('social', 'Social Media'),
        ('friend', 'Friend / Colleague'),
        ('google', 'Google Search'),
        ('email', 'Email Newsletter'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
    ]

    workshop = models.ForeignKey(WorkshopCard, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrollments')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, blank=True)
    referral = models.CharField(max_length=20, choices=REFERRAL_CHOICES, blank=True)
    message = models.TextField(blank=True)
    agreed_to_terms = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Workshop Enrollment'
        verbose_name_plural = 'Workshop Enrollments'
        unique_together = [('workshop', 'email')]

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class PricingPlan(models.Model):
    PLAN_ICON_CHOICES = [
        ('basic', 'Basic (People)'),
        ('pro', 'Pro (Briefcase)'),
        ('enterprise', 'Enterprise (Home)'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=100)
    icon_type = models.CharField(max_length=20, choices=PLAN_ICON_CHOICES, default='basic')
    description = models.CharField(max_length=300)
    monthly_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    yearly_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    monthly_original = models.DecimalField(max_digits=8, decimal_places=2, default=0, blank=True)
    yearly_original = models.DecimalField(max_digits=8, decimal_places=2, default=0, blank=True)
    is_featured = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    cta_label = models.CharField(max_length=50, default='Get Started')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Pricing Plan'
        verbose_name_plural = 'Pricing Plans'

    def __str__(self):
        return self.name


class PricingFeature(models.Model):
    plan = models.ForeignKey(PricingPlan, on_delete=models.CASCADE, related_name='features')
    feature = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.plan.name}: {self.feature}"


# ═══════════════════════════════════════════════════════════════════════════════
# 10. SEO & REDIRECTS
# ═══════════════════════════════════════════════════════════════════════════════

class SEOData(models.Model):
    """Custom SEO overrides per path."""
    path = models.CharField(max_length=255, unique=True, help_text="e.g. / or /projects/ or /tools/")
    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()
    canonical_url = models.URLField(blank=True)
    og_title = models.CharField(max_length=255, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.ImageField(upload_to='seo/', blank=True, null=True)
    robots = models.CharField(max_length=100, default='index, follow', help_text="e.g. index, follow or noindex, nofollow")
    schema_type = models.CharField(max_length=60, blank=True, default='Auto', help_text="Schema.org type: WebSite, Product, Article, Course, FAQPage, Organization")
    custom_json_ld = models.TextField(blank=True, help_text="Optional custom Schema.org JSON-LD override")
    is_indexable = models.BooleanField(default=True, help_text="Search engine index status toggle")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'SEO Metadata'
        verbose_name_plural = 'SEO Metadata'

    def __str__(self):
        return f"SEO for {self.path}"


class Redirect(models.Model):
    """301 / 302 permanent redirects for preserved legacy URLs."""
    STATUS_CHOICES = [
        (301, '301 Permanent Redirect'),
        (302, '302 Temporary Redirect'),
    ]

    old_path = models.CharField(max_length=255, unique=True, help_text="e.g. /old-project/ or /portfolio/")
    new_path = models.CharField(max_length=255, help_text="e.g. /projects/ or /projects/my-slug/")
    status_code = models.PositiveIntegerField(choices=STATUS_CHOICES, default=301)
    is_active = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'URL Redirect'
        verbose_name_plural = 'URL Redirects'

    def __str__(self):
        return f"{self.old_path} -> {self.new_path} ({self.status_code})"


# ═══════════════════════════════════════════════════════════════════════════════
# 12. AI CHATBOT DATA & CONVERSATION TELEMETRY
# ═══════════════════════════════════════════════════════════════════════════════

class ChatbotConversation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active Chatting'),
        ('lead', 'Lead Captured 🎯'),
        ('resolved', 'Resolved / Completed'),
        ('archived', 'Archived'),
    ]

    session_id = models.CharField(max_length=100, db_index=True, help_text="Unique browser session token")
    user_name = models.CharField(max_length=150, blank=True, default='')
    user_email = models.EmailField(blank=True, default='')
    user_phone = models.CharField(max_length=50, blank=True, default='')
    service_interest = models.CharField(max_length=200, blank=True, default='', help_text="Detected interest (e.g. AI Projects, Mentorship)")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    page_url = models.CharField(max_length=500, blank=True, default='/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    admin_notes = models.TextField(blank=True, help_text="Internal staff notes for follow-up")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Chatbot Conversation'
        verbose_name_plural = 'Chatbot Conversations'

    def __str__(self):
        ident = self.user_email or self.user_name or f"Session {self.session_id[:8]}"
        return f"{ident} ({self.messages.count()} msgs) — {self.get_status_display()}"


class ChatbotMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'Visitor / User'),
        ('bot', 'AI Chatbot Assistant'),
        ('agent', 'Staff Agent'),
    ]

    conversation = models.ForeignKey(ChatbotConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES, default='user')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Chatbot Message'
        verbose_name_plural = 'Chatbot Messages'

    def __str__(self):
        return f"[{self.sender.upper()}] {self.message[:60]}"


# ═══════════════════════════════════════════════════════════════════════════════
# 11. ADMIN GUIDE & OPERATIONAL MANUAL
# ═══════════════════════════════════════════════════════════════════════════════

class AdminGuideNote(models.Model):
    """Custom operational notes, checklists, and documentation items managed by admins."""
    CATEGORY_CHOICES = [
        ('general', '🌟 General / Platform Overview'),
        ('branding', '⚙️ Branding & Site Settings'),
        ('navigation', '🎨 Navigation & Mega Menu'),
        ('projects', '🚀 Projects & Showcase'),
        ('tools', '🛠️ AI Tools Directory'),
        ('services', '💼 Services & Case Studies'),
        ('workshops', '🎓 3-Day Bootcamps'),
        ('blog', '📝 Blog & Content'),
        ('crm', '📬 CRM, Leads & Chatbot'),
        ('seo', '🔍 SEO & Redirects'),
        ('checklist', '📋 Operational Checklist'),
    ]

    title = models.CharField(max_length=200, help_text="Title of this guide note or task")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')
    content = models.TextField(help_text="Detailed instructions, operational steps, or reference notes")
    action_url = models.CharField(max_length=300, blank=True, default='', help_text="Optional admin or site URL to take action directly")
    action_label = models.CharField(max_length=100, blank=True, default='', help_text="Button text (e.g. 'Edit Site Settings', 'Add Project')")
    is_pinned = models.BooleanField(default=False, help_text="Pin to the top of the guide")
    is_completed = models.BooleanField(default=False, help_text="Mark checklist item as completed")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers appear first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', 'order', '-created_at']
        verbose_name = 'Admin Guide Note'
        verbose_name_plural = 'Admin Guide Notes'

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"


