from django.contrib import admin
from django.utils.html import format_html, format_html_join
from .models import (
    Project, ProjectImage, ProjectHighlight, ProjectDiagram,
    ProjectTimelinePhase, ProjectFeature,
    WorkshopCard, WorkshopDay, PricingPlan,
    PricingFeature, ContactMessage, ProjectGateLead,
    IdeaSubmission, WorkshopEnrollment,
    BlogPost, BlogSection,
)


# ── Project Inline Admins ─────────────────────────────────────────────────────

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3
    fields = ('image', 'image_preview', 'caption', 'alt', 'order')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:52px;object-fit:cover;'
                'border-radius:4px;border:1px solid #334155;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Preview'


class ProjectHighlightInline(admin.TabularInline):
    model = ProjectHighlight
    extra = 3
    fields = ('icon', 'value', 'label', 'order')


class ProjectDiagramInline(admin.TabularInline):
    model = ProjectDiagram
    extra = 2
    fields = ('image', 'diagram_preview', 'label', 'title', 'desc', 'order')
    readonly_fields = ('diagram_preview',)

    def diagram_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="width:100px;height:64px;object-fit:cover;'
                'border-radius:4px;border:1px solid #334155;" />',
                obj.image.url
            )
        return '—'
    diagram_preview.short_description = 'Preview'


class ProjectTimelinePhaseInline(admin.TabularInline):
    model = ProjectTimelinePhase
    extra = 3
    fields = ('phase', 'date', 'title', 'desc', 'order')


class ProjectFeatureInline(admin.TabularInline):
    model = ProjectFeature
    extra = 4
    fields = ('text', 'order')
    verbose_name = "What's Included Feature"
    verbose_name_plural = "What's Included Features"


# ── Projects ──────────────────────────────────────────────────────────────────

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'tag_list', 'has_detailed_content',
        'show_on_index', 'is_active', 'order', 'image_preview', 'created_at'
    )
    list_display_links = ('title',)
    list_editable = ('show_on_index', 'is_active', 'order')
    list_filter = ('category', 'show_on_index', 'is_active')
    search_fields = ('title', 'description', 'tags')
    ordering = ('order', '-created_at')
    inlines = [
        ProjectImageInline,
        ProjectHighlightInline,
        ProjectDiagramInline,
        ProjectTimelinePhaseInline,
        ProjectFeatureInline,
    ]
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'description', 'detailed_description', 'tags', 'category')
        }),
        ('Hero Media', {
            'fields': ('image', 'image_url', 'youtube_url'),
            'description': (
                'Main project image — upload a file OR paste an external URL (upload takes priority). '
                'Add a YouTube URL to show a video player instead of the image.'
            ),
        }),
        ('Files & Downloads', {
            'fields': ('download_file',),
        }),
        ('Links', {
            'fields': ('project_url', 'github_url', 'case_study_url'),
        }),
        ('Project Meta', {
            'fields': ('year', 'role', 'duration', 'team_size'),
            'description': 'Shown in the sidebar Details panel.',
        }),
        ('Pricing', {
            'fields': ('price', 'price_label'),
            'description': (
                'Set a price label (e.g. ₹2,999 or Free). '
                'Add included features in the "What\'s Included Features" inline below.'
            ),
        }),
        ('Display Settings', {
            'fields': ('show_on_index', 'is_active', 'order'),
            'description': (
                '<strong>show_on_index</strong>: Also display this card in the homepage projects section.<br>'
                '<strong>is_active</strong>: Show on the Projects page.'
            ),
        }),
    )

    def tag_list(self, obj):
        return format_html_join(
            '', '<span style="background:#1e293b;color:#94a3b8;padding:2px 8px;'
                'border-radius:99px;font-size:11px;margin-right:4px;">{}</span>',
            ((t,) for t in obj.get_tags_list()[:3])
        ) or '—'
    tag_list.short_description = 'Tags'

    def has_detailed_content(self, obj):
        has_detail = bool(
            obj.detailed_description
            or obj.detail_images.exists()
            or obj.download_file
            or obj.price_features.exists()
        )
        return format_html(
            '<span style="color:{};font-weight:bold;">{}</span>',
            '#10b981' if has_detail else '#6b7280',
            '✓' if has_detail else '—'
        )
    has_detailed_content.short_description = 'Detail Page'

    def image_preview(self, obj):
        src = obj.get_image_src()
        if src:
            return format_html(
                '<img src="{}" style="width:60px;height:40px;object-fit:cover;border-radius:4px;" />',
                src
            )
        return '—'
    image_preview.short_description = 'Preview'


# ── Workshop ───────────────────────────────────────────────────────────────────

class WorkshopDayInline(admin.TabularInline):
    model = WorkshopDay
    extra = 4
    fields = ('day_number', 'title', 'date_label', 'description', 'topics', 'outcome')


@admin.register(WorkshopCard)
class WorkshopCardAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'date', 'seats', 'price_display',
        'enrollment_count', 'is_featured', 'is_active', 'order'
    )
    list_editable = ('is_featured', 'is_active', 'order')
    list_filter = ('is_featured', 'is_active')
    search_fields = ('title', 'description')
    inlines = [WorkshopDayInline]
    fieldsets = (
        ('Workshop Info', {
            'fields': ('title', 'subtitle', 'description')
        }),
        ('Schedule', {
            'fields': ('date', 'time', 'seats', 'mode')
        }),
        ('Pricing', {
            'fields': ('price', 'price_label', 'enroll_url')
        }),
        ('Display', {
            'fields': ('is_active', 'is_featured', 'order')
        }),
    )

    def price_display(self, obj):
        if obj.price_label:
            return obj.price_label
        if obj.price == 0:
            return 'Free'
        return f'₹{obj.price}'
    price_display.short_description = 'Price'

    def enrollment_count(self, obj):
        count = obj.enrollments.count()
        return format_html(
            '<span style="color:#6366f1;font-weight:600;">{}</span>',
            count
        )
    enrollment_count.short_description = 'Enrolled'


# ── Pricing ────────────────────────────────────────────────────────────────────

class PricingFeatureInline(admin.TabularInline):
    model = PricingFeature
    extra = 5
    fields = ('feature', 'order')


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'monthly_price', 'yearly_price',
        'is_featured', 'is_free', 'is_active', 'order'
    )
    list_editable = ('is_featured', 'is_active', 'order')
    list_filter = ('is_featured', 'is_free', 'is_active')
    inlines = [PricingFeatureInline]
    fieldsets = (
        ('Plan Details', {
            'fields': ('name', 'icon_type', 'description', 'cta_label')
        }),
        ('Pricing', {
            'fields': ('is_free', 'monthly_price', 'monthly_original', 'yearly_price', 'yearly_original')
        }),
        ('Display', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )


# ── Contact Messages ───────────────────────────────────────────────────────────

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subject', 'status', 'created_at')
    list_display_links = ('full_name', 'email')
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email', 'subject', 'message')
    readonly_fields = ('full_name', 'email', 'subject', 'message', 'ip_address', 'created_at')
    ordering = ('-created_at',)
    fieldsets = (
        ('Sender', {
            'fields': ('full_name', 'email', 'ip_address', 'created_at')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Admin', {
            'fields': ('status', 'admin_notes')
        }),
    )

    def has_add_permission(self, request):
        return False


# ── Project Gate Leads ─────────────────────────────────────────────────────────

@admin.register(ProjectGateLead)
class ProjectGateLeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'college_or_org', 'created_at')
    search_fields = ('full_name', 'email', 'college_or_org')
    readonly_fields = ('full_name', 'email', 'college_or_org', 'ip_address', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False


# ── Idea Submissions ───────────────────────────────────────────────────────────

@admin.register(IdeaSubmission)
class IdeaSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'email', 'project_title', 'budget',
        'timeline', 'status', 'created_at'
    )
    list_display_links = ('full_name', 'email')
    list_editable = ('status',)
    list_filter = ('status', 'budget', 'timeline', 'created_at')
    search_fields = ('full_name', 'email', 'project_title', 'description')
    readonly_fields = (
        'full_name', 'email', 'phone', 'project_title',
        'description', 'budget', 'timeline', 'agreed_to_terms',
        'ip_address', 'created_at'
    )
    ordering = ('-created_at',)
    fieldsets = (
        ('Contact', {
            'fields': ('full_name', 'email', 'phone', 'ip_address', 'created_at')
        }),
        ('Project Details', {
            'fields': ('project_title', 'description', 'budget', 'timeline', 'agreed_to_terms')
        }),
        ('Admin', {
            'fields': ('status', 'admin_notes')
        }),
    )

    def has_add_permission(self, request):
        return False


# ── Workshop Enrollments ───────────────────────────────────────────────────────

@admin.register(WorkshopEnrollment)
class WorkshopEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'email', 'phone', 'workshop',
        'experience', 'status', 'created_at'
    )
    list_display_links = ('full_name', 'email')
    list_editable = ('status',)
    list_filter = ('status', 'experience', 'workshop', 'created_at')
    search_fields = ('full_name', 'email', 'phone')
    readonly_fields = (
        'full_name', 'email', 'phone', 'workshop', 'experience',
        'referral', 'message', 'agreed_to_terms', 'ip_address', 'created_at'
    )
    ordering = ('-created_at',)
    fieldsets = (
        ('Enrollee', {
            'fields': ('full_name', 'email', 'phone', 'ip_address', 'created_at')
        }),
        ('Enrollment Details', {
            'fields': ('workshop', 'experience', 'referral', 'message', 'agreed_to_terms')
        }),
        ('Admin', {
            'fields': ('status', 'admin_notes')
        }),
    )

    def has_add_permission(self, request):
        return False


# ── Blog ───────────────────────────────────────────────────────────────────────

class BlogSectionInline(admin.StackedInline):
    model = BlogSection
    extra = 3
    fields = ('heading', 'body', 'code', 'order')


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'published_at', 'read_time',
        'section_count', 'is_featured', 'is_active', 'order', 'swatch'
    )
    list_display_links = ('title',)
    list_editable = ('is_featured', 'is_active', 'order')
    list_filter = ('category', 'is_active', 'is_featured', 'published_at')
    search_fields = ('title', 'excerpt', 'lead')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ('order', '-published_at')
    inlines = [BlogSectionInline]
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'category', 'excerpt', 'lead'),
            'description': (
                'The excerpt is the card summary. The lead is the opening '
                'paragraph on the post page — leave it blank to reuse the excerpt. '
                'Write the body of the post in the Sections below.'
            ),
        }),
        ('Appearance', {
            'fields': (
                'emoji', 'gradient_from', 'gradient_to', 'accent',
                'image', 'image_url',
            ),
            'description': (
                'The card and hero use the emoji on a gradient. Upload an image '
                '(or paste a URL) to use a picture instead.'
            ),
        }),
        ('Meta', {
            'fields': (
                'read_time', 'published_at',
                'author_name', 'author_role', 'author_initials',
            ),
        }),
        ('Display Settings', {
            'fields': ('is_active', 'is_featured', 'order'),
        }),
    )

    def section_count(self, obj):
        return obj.sections.count()
    section_count.short_description = 'Sections'

    def swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:54px;height:24px;'
            'border-radius:6px;background:linear-gradient(135deg,{},{});'
            'text-align:center;line-height:24px;">{}</span>',
            obj.gradient_from, obj.gradient_to, obj.emoji
        )
    swatch.short_description = 'Card'
