import re
from urllib.parse import parse_qs, urlparse
from django.db import models


# ── Projects ──────────────────────────────────────────────────────────────────

class Project(models.Model):
    CATEGORY_CHOICES = [
        ('ml', 'Machine Learning'),
        ('backend', 'Backend'),
        ('data', 'Data'),
        ('cloud', 'Cloud'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    detailed_description = models.TextField(
        blank=True,
        help_text="Detailed description for the project detail page"
    )
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    image_url = models.URLField(
        blank=True,
        help_text="External image URL (used if no uploaded image)"
    )
    tags = models.CharField(
        max_length=300,
        help_text="Comma-separated tags e.g. PyTorch, FastAPI, AWS"
    )
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default='ml'
    )
    project_url = models.URLField(
        blank=True,
        help_text="Link to live project or case study"
    )
    youtube_url = models.URLField(
        blank=True,
        help_text="YouTube demo URL"
    )
    download_file = models.FileField(
        upload_to='project_files/', blank=True, null=True,
        help_text="Downloadable file for this project"
    )

    # ── Project Detail Page Fields ─────────────────────────────────────────────
    subtitle = models.CharField(
        max_length=300, blank=True,
        help_text="Short tagline shown below the title on the detail page"
    )
    year = models.CharField(
        max_length=10, blank=True,
        help_text="Year completed, e.g. 2025"
    )
    role = models.CharField(
        max_length=100, blank=True,
        help_text="Your role, e.g. ML Engineer"
    )
    duration = models.CharField(
        max_length=100, blank=True,
        help_text="Build duration, e.g. 3 Months"
    )
    team_size = models.CharField(
        max_length=100, blank=True, default='Solo Project',
        help_text="Team size, e.g. Solo Project or 3-person team"
    )
    github_url = models.URLField(
        blank=True,
        help_text="GitHub repository URL"
    )
    case_study_url = models.URLField(
        blank=True,
        help_text="Case study PDF or external documentation link"
    )

    # ── Per-Project Pricing ────────────────────────────────────────────────────
    price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, blank=True,
        help_text="Project price (0 = free)"
    )
    price_label = models.CharField(
        max_length=50, blank=True,
        help_text="Display label, e.g. ₹2,999 or Free"
    )

    # Display control
    show_on_index = models.BooleanField(
        default=False,
        help_text="Show this project on the homepage projects section"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Show on projects page"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order (lower = first)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.title

    def get_image_src(self):
        if self.image:
            return self.image.url
        return self.image_url or ''

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_youtube_embed_url(self):
        """Return a YouTube embed URL from watch, short, shorts, or embed link."""
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

    def get_youtube_video_id(self):
        """Extract the 11-char video ID from the YouTube URL."""
        embed = self.get_youtube_embed_url()
        if not embed:
            return ''
        m = re.search(r'/embed/([A-Za-z0-9_-]{11})', embed)
        return m.group(1) if m else ''

    def get_category_list(self):
        return self.category


# ── Project Related Tables ─────────────────────────────────────────────────────

class ProjectImage(models.Model):
    """Detail/screenshot images uploaded directly from admin."""
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='detail_images'
    )
    image = models.ImageField(upload_to='projects/detail/')
    caption = models.CharField(max_length=300, blank=True)
    alt = models.CharField(
        max_length=200, blank=True,
        help_text="Alt text (defaults to project title if left blank)"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Detail Image'
        verbose_name_plural = 'Detail Images'

    def __str__(self):
        return f"{self.project.title} — image {self.order}"

    @property
    def url(self):
        return self.image.url if self.image else ''


class ProjectHighlight(models.Model):
    """Key metric highlight cards shown in the detail page hero area."""
    ICON_CHOICES = [
        ('chart', 'Bar Chart'),
        ('users', 'Users / Team'),
        ('clock', 'Clock / Time'),
        ('star', 'Star / Rating'),
        ('bolt', 'Bolt / Speed'),
    ]
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='highlights'
    )
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='chart')
    value = models.CharField(max_length=100, help_text="e.g. 94% or 3 Months")
    label = models.CharField(max_length=100, help_text="e.g. Accuracy or Build Time")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Key Highlight'
        verbose_name_plural = 'Key Highlights'

    def __str__(self):
        return f"{self.project.title} — {self.label}: {self.value}"


class ProjectDiagram(models.Model):
    """Architecture / system diagram images."""
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='diagrams'
    )
    image = models.ImageField(upload_to='projects/diagrams/')
    label = models.CharField(
        max_length=100, blank=True, default='Architecture',
        help_text="Short badge label, e.g. Architecture, Data Flow"
    )
    title = models.CharField(max_length=200, help_text="Diagram title")
    desc = models.TextField(blank=True, help_text="Short description of the diagram")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Architecture Diagram'
        verbose_name_plural = 'Architecture Diagrams'

    def __str__(self):
        return f"{self.project.title} — {self.title}"

    @property
    def url(self):
        return self.image.url if self.image else ''


class ProjectTimelinePhase(models.Model):
    """Build timeline phases for the project detail page."""
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='timeline_phases'
    )
    phase = models.CharField(
        max_length=100, help_text="Phase label, e.g. Phase 01"
    )
    date = models.CharField(
        max_length=100, help_text="Date string, e.g. Jan 2025"
    )
    title = models.CharField(max_length=200, help_text="Phase title, e.g. Research & Planning")
    desc = models.TextField(blank=True, help_text="What happened in this phase")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Timeline Phase'
        verbose_name_plural = 'Timeline Phases'

    def __str__(self):
        return f"{self.project.title} — {self.phase}: {self.title}"


class ProjectFeature(models.Model):
    """What's included bullet points shown in the pricing/CTA section."""
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='price_features'
    )
    text = models.CharField(max_length=300, help_text="e.g. Full source code, Docker setup")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "What's Included Feature"
        verbose_name_plural = "What's Included Features"

    def __str__(self):
        return f"{self.project.title} — {self.text}"


# ── Workshop ──────────────────────────────────────────────────────────────────

class WorkshopCard(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    date = models.CharField(max_length=100, help_text="e.g. May 10 – 13, 2026")
    time = models.CharField(max_length=100, help_text="e.g. 10 AM – 5 PM IST")
    seats = models.PositiveIntegerField(default=30)
    mode = models.CharField(max_length=100, default="Online (Live)")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_label = models.CharField(
        max_length=50, blank=True,
        help_text="e.g. Free, ₹999"
    )
    enroll_url = models.URLField(blank=True, help_text="Enrollment / registration link")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Highlight this workshop")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Workshop Card'
        verbose_name_plural = 'Workshop Cards'

    def __str__(self):
        return self.title


class WorkshopDay(models.Model):
    workshop = models.ForeignKey(
        WorkshopCard, on_delete=models.CASCADE, related_name='days'
    )
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    date_label = models.CharField(
        max_length=100, blank=True,
        help_text="e.g. Sunday, May 10"
    )
    description = models.TextField()
    topics = models.TextField(
        blank=True,
        default='',
        help_text="Enter one topic per line, e.g.:\nPython Crash Course for ML\nNumPy & Pandas Deep Dive"
    )
    outcome = models.CharField(
        max_length=300, blank=True,
        help_text="Key outcome for this day"
    )

    class Meta:
        ordering = ['day_number']
        verbose_name = 'Workshop Day'
        verbose_name_plural = 'Workshop Days'

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"


# ── Pricing ───────────────────────────────────────────────────────────────────

class PricingPlan(models.Model):
    PLAN_ICON_CHOICES = [
        ('basic', 'Basic (People)'),
        ('pro', 'Pro (Briefcase)'),
        ('enterprise', 'Enterprise (Home)'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=100)
    icon_type = models.CharField(
        max_length=20, choices=PLAN_ICON_CHOICES, default='basic'
    )
    description = models.CharField(max_length=300)
    monthly_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    yearly_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    monthly_original = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, blank=True
    )
    yearly_original = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, blank=True
    )
    is_featured = models.BooleanField(default=False, help_text="Show 'Popular' badge")
    is_free = models.BooleanField(default=False, help_text="Display price as 'Free'")
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
    plan = models.ForeignKey(
        PricingPlan, on_delete=models.CASCADE, related_name='features'
    )
    feature = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.plan.name}: {self.feature}"


# ── Contact Message ───────────────────────────────────────────────────────────

class ContactMessage(models.Model):
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
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='new'
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes (not visible to user)"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.full_name} — {self.subject or 'No subject'} ({self.created_at.strftime('%d %b %Y')})"


# ── Project Gate Lead ─────────────────────────────────────────────────────────

class ProjectGateLead(models.Model):
    """Captures leads from the 'View all projects' gate modal."""
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


# ── Idea Submission ───────────────────────────────────────────────────────────

class IdeaSubmission(models.Model):
    """Captures submissions from the 'Share Your Idea' modal."""
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
    budget = models.CharField(
        max_length=20, choices=BUDGET_CHOICES, blank=True
    )
    timeline = models.CharField(
        max_length=20, choices=TIMELINE_CHOICES, blank=True
    )
    agreed_to_terms = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='new'
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes (not visible to user)"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Idea Submission'
        verbose_name_plural = 'Idea Submissions'

    def __str__(self):
        return f"{self.full_name} — {self.project_title} ({self.created_at.strftime('%d %b %Y')})"


# ── Workshop Enrollment ───────────────────────────────────────────────────────

class WorkshopEnrollment(models.Model):
    """Captures enrollments from the workshop enroll modal."""
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

    workshop = models.ForeignKey(
        WorkshopCard, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='enrollments'
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    experience = models.CharField(
        max_length=20, choices=EXPERIENCE_CHOICES, blank=True
    )
    referral = models.CharField(
        max_length=20, choices=REFERRAL_CHOICES, blank=True
    )
    message = models.TextField(blank=True, help_text="Optional message from the enrollee")
    agreed_to_terms = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes (not visible to user)"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Workshop Enrollment'
        verbose_name_plural = 'Workshop Enrollments'
        unique_together = [('workshop', 'email')]

    def __str__(self):
        workshop_title = self.workshop.title if self.workshop else 'General'
        return f"{self.full_name} → {workshop_title} ({self.created_at.strftime('%d %b %Y')})"
