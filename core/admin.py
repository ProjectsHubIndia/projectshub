import csv
from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import (
    SiteSettings, NavigationItem, MegaMenuTag, SocialLink, StatItem,
    ProjectCategory, Technology, Project, ProjectImage, ProjectHighlight,
    ProjectDiagram, ProjectTimelinePhase, ProjectFeature,
    ToolCategory, AITool,
    Service, ServiceFeature,
    CaseStudy, CaseStudyMetric, CaseStudyTechnology,
    Testimonial, FAQCategory, FAQ,
    BlogCategory, Tag, BlogPost, BlogSection,
    ContactInquiry, ContactMessage, ProjectGateLead,
    IdeaSubmission, WorkshopCard, WorkshopDay, WorkshopEnrollment,
    PricingPlan, PricingFeature,
    SEOData, Redirect,
    ChatbotConversation, ChatbotMessage,
    AdminGuideNote
)

admin.site.site_header = "ProjectsHub Administration"
admin.site.site_title = "ProjectsHub Admin"
admin.site.index_title = "ProjectsHub Control Dashboard"


def export_as_csv_action(description="Export selected to CSV", fields=None, exclude=None):
    """Reusable CSV export action generator for any ModelAdmin."""
    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta
        field_names = fields or [f.name for f in opts.fields if not exclude or f.name not in exclude]
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={opts.model_name}_export.csv'
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            row = []
            for field in field_names:
                val = getattr(obj, field, '')
                if callable(val):
                    val = val()
                row.append(str(val) if val is not None else '')
            writer.writerow(row)
        return response
    export_as_csv.short_description = description
    return export_as_csv


# ── Inlines ───────────────────────────────────────────────────────────────────

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'caption', 'alt', 'order')


class ProjectHighlightInline(admin.TabularInline):
    model = ProjectHighlight
    extra = 1
    fields = ('icon', 'value', 'label', 'order')


class ProjectDiagramInline(admin.TabularInline):
    model = ProjectDiagram
    extra = 1
    fields = ('image', 'label', 'title', 'desc', 'order')


class ProjectTimelinePhaseInline(admin.TabularInline):
    model = ProjectTimelinePhase
    extra = 1
    fields = ('phase', 'date', 'title', 'desc', 'order')


class ProjectFeatureInline(admin.TabularInline):
    model = ProjectFeature
    extra = 1
    fields = ('text', 'order')


class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 2
    fields = ('title', 'description', 'icon', 'order')


class CaseStudyMetricInline(admin.TabularInline):
    model = CaseStudyMetric
    extra = 2
    fields = ('label', 'value', 'description', 'order')


class CaseStudyTechnologyInline(admin.TabularInline):
    model = CaseStudyTechnology
    extra = 1
    fields = ('technology',)


class BlogSectionInline(admin.StackedInline):
    model = BlogSection
    extra = 1
    fields = ('heading', 'body', 'code', 'order')


# ── Core & Site Settings ──────────────────────────────────────────────────────

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'primary_email', 'phone', 'location', 'updated_at')
    fieldsets = (
        ('Branding & Titles', {
            'fields': ('site_name', 'tagline', 'hero_headline_prefix', 'hero_headline_highlight', 'hero_subtitle')
        }),
        ('Contact Info', {
            'fields': ('primary_email', 'phone', 'whatsapp_number', 'location', 'response_time')
        }),
        ('Logos', {
            'fields': ('logo_dark', 'logo_light')
        }),
        ('Mega Menu "Our Work" Footer Bar', {
            'fields': ('mega_popular_label', 'mega_browse_all_text', 'mega_browse_all_url'),
            'description': 'Configure the bottom bar of the "Our Work" dropdown menu (popular tags label, CTA button text, and link).'
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.objects.first()
        if obj:
            from django.shortcuts import redirect
            return redirect(f'/admin/core/sitesettings/{obj.pk}/change/')
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'url', 'badge_preview', 'order', 'is_active', 'open_in_new_tab')
    list_filter = ('group', 'is_active', 'badge_color')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'url', 'description', 'badge_text')
    fieldsets = (
        ('Navigation Link', {
            'fields': ('title', 'url', 'group', 'parent'),
            'description': 'Main target and hierarchy grouping for this navigation element.'
        }),
        ('Mega Menu UI/UX Presentation', {
            'fields': ('description', 'badge_text', 'badge_color', 'image', 'icon_svg'),
            'description': 'Visual card elements rendered in the Mega Menu (badges, card thumbnails, icons, and descriptions).'
        }),
        ('Behavior & Ordering', {
            'fields': ('order', 'is_active', 'open_in_new_tab'),
        }),
    )

    def badge_preview(self, obj):
        if not obj.badge_text:
            return "—"
        color_map = {
            'cyan': '#0284c7',
            'emerald': '#059669',
            'purple': '#7c3aed',
            'amber': '#d97706',
            'rose': '#e11d48',
            'blue': '#2563eb',
        }
        bg = color_map.get(obj.badge_color, '#0284c7')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;">{}</span>',
            bg, obj.badge_text
        )
    badge_preview.short_description = 'Badge'


@admin.register(MegaMenuTag)
class MegaMenuTagAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'order', 'is_active', 'open_in_new_tab')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'url')
    fields = ('title', 'url', 'order', 'is_active', 'open_in_new_tab')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(group='popular_tags')

    def save_model(self, request, obj, form, change):
        obj.group = 'popular_tags'
        super().save_model(request, obj, form, change)



@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('platform', 'label', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(StatItem)
class StatItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'section', 'icon', 'order', 'is_active')
    list_filter = ('section', 'is_active')
    list_editable = ('value', 'order', 'is_active')


# ── Projects, Categories, Tech ────────────────────────────────────────────────

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'website_url', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)
    search_fields = ('name', 'slug')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'image_preview', 'title', 'category_ref', 'tag_preview', 'price_badge',
        'live_link', 'show_on_index', 'featured', 'is_active', 'order'
    )
    list_editable = ('show_on_index', 'featured', 'is_active', 'order')
    list_filter = ('category_ref', 'featured', 'show_on_index', 'is_active', 'difficulty')
    search_fields = ('title', 'description', 'tags', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('technologies',)
    actions = ['duplicate_project', export_as_csv_action('Export selected projects to CSV')]
    inlines = [
        ProjectHighlightInline,
        ProjectImageInline,
        ProjectDiagramInline,
        ProjectTimelinePhaseInline,
        ProjectFeatureInline,
    ]
    fieldsets = (
        ('Overview', {
            'fields': ('title', 'slug', 'subtitle', 'category', 'category_ref', 'technologies', 'tags', 'difficulty')
        }),
        ('Descriptions', {
            'fields': ('description', 'detailed_description')
        }),
        ('Media & Files', {
            'fields': ('image', 'thumbnail', 'image_url', 'youtube_url', 'download_file')
        }),
        ('External Links & Pricing', {
            'fields': ('project_url', 'github_url', 'demo_url', 'external_url', 'price', 'price_label')
        }),
        ('Visibility & Publishing', {
            'fields': ('show_on_index', 'featured', 'is_active', 'is_published', 'order')
        }),
        ('SEO Metadata', {
            'classes': ('collapse',),
            'fields': ('meta_title', 'meta_description', 'canonical_url', 'og_title', 'og_description', 'og_image')
        }),
    )

    def image_preview(self, obj):
        img = obj.thumbnail or obj.image
        if img:
            return format_html(
                '<img src="{}" style="width: 52px; height: 32px; object-fit: cover; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);" />',
                img.url
            )
        return format_html('<span style="color:#94a3b8;font-size:11px;">—</span>')
    image_preview.short_description = 'Media'

    def tag_preview(self, obj):
        tags = obj.get_tags_list()
        return ', '.join(tags[:4]) if tags else '—'
    tag_preview.short_description = 'Tech Tags'

    def price_badge(self, obj):
        label = obj.price_label or ('Free' if not obj.price else f'₹{obj.price}')
        is_free = 'free' in label.lower()
        bg = '#ecfdf5' if is_free else '#f1f5f9'
        color = '#059669' if is_free else '#334155'
        return format_html(
            '<span style="background:{};color:{};font-weight:700;font-size:11px;padding:2px 8px;border-radius:99px;border:1px solid rgba(0,0,0,0.06);">{}</span>',
            bg, color, label
        )
    price_badge.short_description = 'Pricing'

    def live_link(self, obj):
        if obj.slug:
            return format_html(
                '<a href="/projects/{}/" target="_blank" style="display:inline-flex;align-items:center;gap:3px;font-size:11px;font-weight:700;color:#4f46e5;background:#eef2ff;padding:3px 8px;border-radius:6px;text-decoration:none;border:1px solid #c7d2fe;">↗ Live</a>',
                obj.slug
            )
        return '—'
    live_link.short_description = 'Preview'

    def duplicate_project(self, request, queryset):
        count = 0
        for project in queryset:
            orig_pk = project.pk
            orig_title = project.title
            orig_slug = project.slug or 'project'
            project.pk = None
            project.id = None
            project.title = f"{orig_title} (Copy)"
            base_slug = f"{orig_slug}-copy"
            new_slug = base_slug
            idx = 1
            while Project.objects.filter(slug=new_slug).exists():
                new_slug = f"{base_slug}-{idx}"
                idx += 1
            project.slug = new_slug
            project.is_published = False
            project.show_on_index = False
            project.save()
            # Copy M2M technologies & child inlines
            orig_obj = Project.objects.get(pk=orig_pk)
            project.technologies.set(orig_obj.technologies.all())
            for h in orig_obj.highlights.all():
                h.pk = None
                h.id = None
                h.project = project
                h.save()
            for img in orig_obj.detail_images.all():
                img.pk = None
                img.id = None
                img.project = project
                img.save()
            for d in orig_obj.diagrams.all():
                d.pk = None
                d.id = None
                d.project = project
                d.save()
            for tp in orig_obj.timeline_phases.all():
                tp.pk = None
                tp.id = None
                tp.project = project
                tp.save()
            for pf in orig_obj.price_features.all():
                pf.pk = None
                pf.id = None
                pf.project = project
                pf.save()
            count += 1
        self.message_user(request, f"Successfully duplicated {count} project(s) with all sections as draft.")
    duplicate_project.short_description = "Duplicate selected project(s) as draft"


# ── Free AI Tools ─────────────────────────────────────────────────────────────

@admin.register(ToolCategory)
class ToolCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)


@admin.register(AITool)
class AIToolAdmin(admin.ModelAdmin):
    list_display = ('tool_preview', 'name', 'category', 'external_link', 'is_free', 'featured', 'is_published', 'sort_order')
    list_editable = ('is_free', 'featured', 'is_published', 'sort_order')
    list_filter = ('category', 'is_free', 'is_published', 'featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    actions = [
        'mark_published', 'mark_unpublished', 'mark_featured', 'mark_unfeatured',
        export_as_csv_action('Export tools to CSV')
    ]

    def mark_published(self, request, queryset):
        queryset.update(is_published=True)
    mark_published.short_description = "Publish selected tools"

    def mark_unpublished(self, request, queryset):
        queryset.update(is_published=False)
    mark_unpublished.short_description = "Unpublish (draft) selected tools"

    def mark_featured(self, request, queryset):
        queryset.update(featured=True)
    mark_featured.short_description = "Feature selected tools"

    def mark_unfeatured(self, request, queryset):
        queryset.update(featured=False)
    mark_unfeatured.short_description = "Unfeature selected tools"

    def tool_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 32px; height: 32px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        icon_or_emoji = obj.icon or '⚡'
        if icon_or_emoji.startswith('fa-') or 'fa-' in icon_or_emoji:
            return format_html('<i class="{}" style="font-size:18px;color:#6366f1;"></i>', icon_or_emoji)
        return format_html('<span style="font-size: 18px;">{}</span>', icon_or_emoji)
    tool_preview.short_description = 'Icon'

    def external_link(self, obj):
        if obj.external_url:
            return format_html(
                '<a href="{}" target="_blank" style="display:inline-flex;align-items:center;gap:3px;font-size:11px;font-weight:700;color:#0284c7;background:#f0f9ff;padding:3px 8px;border-radius:6px;text-decoration:none;border:1px solid #bae6fd;">↗ Open</a>',
                obj.external_url
            )
        return '—'
    external_link.short_description = 'Link'


# ── Services ──────────────────────────────────────────────────────────────────

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_audience', 'slug', 'icon', 'is_published', 'sort_order')
    list_editable = ('is_published', 'sort_order')
    list_filter = ('target_audience', 'is_published')
    search_fields = ('title', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceFeatureInline]


@admin.register(ServiceFeature)
class ServiceFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'service', 'icon', 'order')
    list_editable = ('order',)
    list_filter = ('service',)
    search_fields = ('title', 'description', 'service__title')
    ordering = ('service', 'order')


# ── Case Studies ──────────────────────────────────────────────────────────────

@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'client', 'industry', 'timeline', 'is_featured', 'is_published', 'live_link', 'sort_order')
    list_editable = ('is_featured', 'is_published', 'sort_order')
    list_filter = ('industry', 'is_featured', 'is_published')
    search_fields = ('title', 'client', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CaseStudyMetricInline, CaseStudyTechnologyInline]
    actions = [export_as_csv_action('Export case studies to CSV')]

    def image_preview(self, obj):
        img = obj.featured_image
        if img:
            return format_html(
                '<img src="{}" style="width: 52px; height: 32px; object-fit: cover; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);" />',
                img.url
            )
        emoji = obj.icon_emoji or '📁'
        return format_html('<span style="font-size: 20px; display: inline-block; width: 32px; text-align: center;">{}</span>', emoji)
    image_preview.short_description = 'Preview'

    def live_link(self, obj):
        if obj.slug:
            return format_html(
                '<a href="/case-studies/#{}" target="_blank" style="display:inline-flex;align-items:center;gap:3px;font-size:11px;font-weight:700;color:#059669;background:#ecfdf5;padding:3px 8px;border-radius:6px;text-decoration:none;border:1px solid #a7f3d0;">↗ Live</a>',
                obj.slug
            )
        return '—'
    live_link.short_description = 'Preview'



# ── Testimonials ──────────────────────────────────────────────────────────────

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'role', 'rating_stars', 'avatar_preview', 'is_featured', 'is_published', 'sort_order')
    list_editable = ('is_featured', 'is_published', 'sort_order')
    list_filter = ('rating', 'is_featured', 'is_published')
    search_fields = ('name', 'role', 'content')

    def rating_stars(self, obj):
        stars = '★' * (obj.rating or 5)
        return format_html('<span style="color:#f59e0b;letter-spacing:2px;font-size:14px;">{}</span>', stars)
    rating_stars.short_description = 'Rating'

    def avatar_preview(self, obj):
        color = obj.avatar_color or '#6366f1'
        initial = (obj.name or 'A')[:1].upper()
        return format_html(
            '<div style="width:28px;height:28px;border-radius:50%;background:{};color:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;">{}</div>',
            color, initial
        )
    avatar_preview.short_description = 'Avatar'


# ── FAQs ──────────────────────────────────────────────────────────────────────

@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'sort_order', 'is_published')
    list_editable = ('sort_order', 'is_published')
    list_filter = ('category', 'is_published')
    search_fields = ('question', 'answer')


# ── Blog ──────────────────────────────────────────────────────────────────────

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        'image_preview', 'title', 'category', 'author_name', 'read_time_badge',
        'published_at', 'is_featured', 'is_published', 'live_link', 'order'
    )
    list_editable = ('is_featured', 'is_published', 'order')
    list_filter = ('category', 'is_featured', 'is_published', 'published_at')
    search_fields = ('title', 'excerpt', 'author_name')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    inlines = [BlogSectionInline]
    actions = ['mark_published', 'mark_draft', 'duplicate_post', export_as_csv_action('Export blog posts to CSV')]

    def duplicate_post(self, request, queryset):
        count = 0
        for post in queryset:
            orig_pk = post.pk
            orig_title = post.title
            orig_slug = post.slug or 'post'
            post.pk = None
            post.id = None
            post.title = f"{orig_title} (Copy)"
            base_slug = f"{orig_slug}-copy"
            new_slug = base_slug
            idx = 1
            while BlogPost.objects.filter(slug=new_slug).exists():
                new_slug = f"{base_slug}-{idx}"
                idx += 1
            post.slug = new_slug
            post.is_published = False
            post.is_featured = False
            post.save()
            orig_obj = BlogPost.objects.get(pk=orig_pk)
            post.tags.set(orig_obj.tags.all())
            for sec in orig_obj.sections.all():
                sec.pk = None
                sec.id = None
                sec.post = post
                sec.save()
            count += 1
        self.message_user(request, f"Successfully duplicated {count} blog post(s) as draft.")
    duplicate_post.short_description = "Duplicate selected post(s) as draft"

    def image_preview(self, obj):
        img = obj.featured_image or obj.image
        if img:
            return format_html(
                '<img src="{}" style="width: 52px; height: 32px; object-fit: cover; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);" />',
                img.url
            )
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width: 52px; height: 32px; object-fit: cover; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);" />',
                obj.image_url
            )
        emoji = obj.emoji or '📝'
        return format_html('<span style="font-size: 20px; display: inline-block; width: 32px; text-align: center;">{}</span>', emoji)
    image_preview.short_description = 'Cover'

    def read_time_badge(self, obj):
        words = len((obj.content or '').split()) + len((obj.excerpt or '').split())
        mins = max(1, round(words / 200))
        return format_html(
            '<span style="font-size:11px;color:#64748b;font-weight:600;background:#f8fafc;padding:2px 6px;border-radius:6px;border:1px solid #e2e8f0;">⏱️ {} min</span>',
            mins
        )
    read_time_badge.short_description = 'Read Time'

    def live_link(self, obj):
        if obj.slug:
            return format_html(
                '<a href="/blog/{}/" target="_blank" style="display:inline-flex;align-items:center;gap:3px;font-size:11px;font-weight:700;color:#7c3aed;background:#f5f3ff;padding:3px 8px;border-radius:6px;text-decoration:none;border:1px solid #ddd6fe;">↗ Live</a>',
                obj.slug
            )
        return '—'
    live_link.short_description = 'Preview'

    def mark_published(self, request, queryset):
        queryset.update(is_published=True)
    mark_published.short_description = "Publish selected posts"

    def mark_draft(self, request, queryset):
        queryset.update(is_published=False)
    mark_draft.short_description = "Unpublish (set to draft)"


# ── Contact Inquiries & Leads ─────────────────────────────────────────────────

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_link', 'phone_link', 'subject', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject', 'message')
    readonly_fields = ('created_at', 'ip_address')
    actions = [
        'mark_contacted', 'mark_in_progress', 'mark_converted',
        'mark_closed', 'mark_spam',
        export_as_csv_action('Export inquiries to CSV')
    ]

    def email_link(self, obj):
        return format_html(
            '<a href="mailto:{}" style="color:#2563eb;font-weight:600;text-decoration:none;">✉️ {}</a>',
            obj.email, obj.email
        )
    email_link.short_description = 'Email'

    def phone_link(self, obj):
        if not obj.phone:
            return format_html('<span style="color:#94a3b8;">—</span>')
        clean = ''.join(c for c in obj.phone if c.isdigit() or c == '+')
        return format_html(
            '<a href="tel:{}" style="color:#059669;font-weight:600;text-decoration:none;">📞 {}</a>',
            clean, obj.phone
        )
    phone_link.short_description = 'Phone'

    def mark_contacted(self, request, queryset):
        queryset.update(status='contacted')
    mark_contacted.short_description = "Mark selected as Contacted"

    def mark_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
    mark_in_progress.short_description = "Mark selected as In Progress"

    def mark_converted(self, request, queryset):
        queryset.update(status='converted')
    mark_converted.short_description = "Mark selected as Converted 🎉"

    def mark_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_closed.short_description = "Mark selected as Closed"

    def mark_spam(self, request, queryset):
        queryset.update(status='spam')
    mark_spam.short_description = "Mark selected as Spam"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email_link', 'subject', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email', 'subject', 'message')
    actions = [export_as_csv_action('Export legacy messages to CSV')]

    def email_link(self, obj):
        return format_html(
            '<a href="mailto:{}" style="color:#2563eb;font-weight:600;text-decoration:none;">✉️ {}</a>',
            obj.email, obj.email
        )
    email_link.short_description = 'Email'


@admin.register(ProjectGateLead)
class ProjectGateLeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email_link', 'college_or_org', 'created_at')
    search_fields = ('full_name', 'email', 'college_or_org')
    actions = [export_as_csv_action('Export gate leads to CSV')]

    def email_link(self, obj):
        return format_html(
            '<a href="mailto:{}" style="color:#2563eb;font-weight:600;text-decoration:none;">✉️ {}</a>',
            obj.email, obj.email
        )
    email_link.short_description = 'Email'


@admin.register(IdeaSubmission)
class IdeaSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'email_link', 'project_title',
        'budget_badge', 'timeline_badge', 'status', 'created_at'
    )
    list_editable = ('status',)
    list_filter = ('status', 'budget', 'timeline', 'created_at')
    search_fields = ('full_name', 'email', 'project_title', 'description')
    actions = [
        'mark_reviewing', 'mark_accepted', 'mark_declined', 'mark_completed',
        export_as_csv_action('Export idea submissions to CSV')
    ]

    def email_link(self, obj):
        return format_html(
            '<a href="mailto:{}?subject=Regarding your project idea: {}" style="color:#2563eb;font-weight:600;text-decoration:none;">✉️ {}</a>',
            obj.email, obj.project_title, obj.email
        )
    email_link.short_description = 'Email'

    def budget_badge(self, obj):
        if not obj.budget:
            return format_html('<span style="color:#94a3b8;">—</span>')
        return format_html(
            '<span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:700;">{}</span>',
            obj.get_budget_display()
        )
    budget_badge.short_description = 'Budget'

    def timeline_badge(self, obj):
        if not obj.timeline:
            return format_html('<span style="color:#94a3b8;">—</span>')
        return format_html(
            '<span style="background:#e0e7ff;color:#3730a3;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:700;">{}</span>',
            obj.get_timeline_display()
        )
    timeline_badge.short_description = 'Timeline'

    def mark_reviewing(self, request, queryset):
        queryset.update(status='reviewing')
    mark_reviewing.short_description = "Mark selected as Reviewing"

    def mark_accepted(self, request, queryset):
        queryset.update(status='accepted')
    mark_accepted.short_description = "Mark selected as Accepted 🎉"

    def mark_declined(self, request, queryset):
        queryset.update(status='declined')
    mark_declined.short_description = "Mark selected as Declined"

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = "Mark selected as Completed"


# ── Workshops & Pricing ───────────────────────────────────────────────────────

class WorkshopDayInline(admin.TabularInline):
    model = WorkshopDay
    extra = 1
    fields = ('day_number', 'title', 'date_label', 'description', 'outcome')


@admin.register(WorkshopCard)
class WorkshopCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'price_label', 'seats', 'is_active', 'is_featured', 'order')
    list_editable = ('is_active', 'is_featured', 'order')
    inlines = [WorkshopDayInline]


@admin.register(WorkshopDay)
class WorkshopDayAdmin(admin.ModelAdmin):
    list_display = ('title', 'workshop', 'day_number', 'date_label', 'outcome')
    list_editable = ('day_number',)
    list_filter = ('workshop',)
    search_fields = ('title', 'description', 'topics', 'outcome', 'workshop__title')
    ordering = ('workshop', 'day_number')


@admin.register(WorkshopEnrollment)
class WorkshopEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email_link', 'workshop', 'experience_badge', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'experience', 'workshop')
    search_fields = ('full_name', 'email', 'phone')
    actions = [
        'mark_confirmed', 'mark_attended', 'mark_cancelled',
        export_as_csv_action('Export workshop enrollments to CSV')
    ]

    def email_link(self, obj):
        return format_html(
            '<a href="mailto:{}?subject=Workshop Enrollment - {}" style="color:#2563eb;font-weight:600;text-decoration:none;">✉️ {}</a>',
            obj.email, getattr(obj.workshop, 'title', 'ProjectsHub Workshop'), obj.email
        )
    email_link.short_description = 'Email'

    def experience_badge(self, obj):
        colors = {
            'beginner': ('#f1f5f9', '#475569'),
            'basic': ('#e0f2fe', '#0369a1'),
            'intermediate': ('#e0e7ff', '#4338ca'),
            'advanced': ('#fef3c7', '#92400e'),
        }
        bg, color = colors.get(obj.experience, ('#f1f5f9', '#475569'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:6px;font-size:11px;font-weight:700;">{}</span>',
            bg, color, obj.get_experience_display()
        )
    experience_badge.short_description = 'Experience'

    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = "Confirm selected enrollments"

    def mark_attended(self, request, queryset):
        queryset.update(status='attended')
    mark_attended.short_description = "Mark selected as Attended"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_cancelled.short_description = "Cancel selected enrollments"


class PricingFeatureInline(admin.TabularInline):
    model = PricingFeature
    extra = 2


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_type', 'monthly_price', 'yearly_price', 'is_featured', 'is_active', 'order')
    list_editable = ('is_featured', 'is_active', 'order')
    inlines = [PricingFeatureInline]


# ── SEO & Redirects ───────────────────────────────────────────────────────────

@admin.register(SEOData)
class SEODataAdmin(admin.ModelAdmin):
    list_display = ('path', 'title_health', 'index_status', 'schema_type', 'updated_at')
    list_filter = ('is_indexable', 'schema_type')
    search_fields = ('path', 'meta_title', 'meta_description')
    actions = ['generate_all_seo_records', 'mark_as_indexable', 'mark_as_noindex']
    fieldsets = (
        ('Route & Index Directives', {
            'fields': ('path', 'canonical_url', 'is_indexable', 'robots'),
            'description': 'Configure route URL, canonical link, and search engine robots indexing directives.'
        }),
        ('Search Metadata', {
            'fields': ('meta_title', 'meta_description'),
            'description': 'Search engine title and meta description snippets.'
        }),
        ('OpenGraph & Social Sharing', {
            'fields': ('og_title', 'og_description', 'og_image'),
        }),
        ('Schema.org Structured Data', {
            'fields': ('schema_type', 'custom_json_ld'),
            'description': 'Schema.org JSON-LD type (WebSite, Product, Article, Course, FAQPage, etc.) or custom JSON-LD payload override.'
        }),
    )

    def title_health(self, obj):
        title = obj.meta_title or '—'
        length = len(obj.meta_title or '')
        bg = '#d1fae5' if 30 <= length <= 65 else ('#fef3c7' if length > 0 else '#fee2e2')
        color = '#065f46' if 30 <= length <= 65 else ('#92400e' if length > 0 else '#991b1b')
        return format_html(
            '<span>{}</span> <span style="background:{};color:{};padding:1px 6px;border-radius:99px;font-size:10px;font-weight:700;margin-left:4px;">{} chars</span>',
            title[:40], bg, color, length
        )
    title_health.short_description = 'Meta Title'

    def index_status(self, obj):
        if obj.is_indexable and 'noindex' not in (obj.robots or ''):
            return format_html(
                '<span style="background:#00a32a;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;">✅ INDEX, FOLLOW</span>'
            )
        return format_html(
            '<span style="background:#d63638;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;">⚠️ NOINDEX</span>'
        )
    index_status.short_description = 'Index Directives'

    @admin.action(description='⚡ Auto-Generate / Synchronize Best SEO & Schema for All Site Routes')
    def generate_all_seo_records(self, request, queryset):
        from core.seo import auto_generate_all_seo_data
        count = auto_generate_all_seo_data()
        self.message_user(request, f"Successfully analyzed and synchronized SEO & Schema.org data for {count} routes.")

    @admin.action(description='Mark selected as Indexable (index, follow)')
    def mark_as_indexable(self, request, queryset):
        queryset.update(is_indexable=True, robots='index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1')
        self.message_user(request, "Selected routes marked as indexable.")

    @admin.action(description='Mark selected as NOINDEX')
    def mark_as_noindex(self, request, queryset):
        queryset.update(is_indexable=False, robots='noindex, nofollow')
        self.message_user(request, "Selected routes marked as NOINDEX.")



@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ('old_path', 'new_path', 'status_badge', 'test_link', 'is_active', 'notes')
    list_editable = ('is_active',)
    search_fields = ('old_path', 'new_path', 'notes')
    list_filter = ('status_code', 'is_active')
    actions = [export_as_csv_action('Export redirects to CSV')]

    def status_badge(self, obj):
        bg = '#d1fae5' if obj.status_code == 301 else '#e0f2fe'
        color = '#065f46' if obj.status_code == 301 else '#0369a1'
        label = '301 Perm' if obj.status_code == 301 else '302 Temp'
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:99px;font-weight:700;font-size:11px;">{}</span>',
            bg, color, label
        )
    status_badge.short_description = 'Type'

    def test_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank" style="display:inline-flex;align-items:center;gap:2px;color:#4f46e5;font-weight:700;font-size:11px;background:#eef2ff;padding:2px 8px;border-radius:6px;text-decoration:none;border:1px solid #c7d2fe;">↗ Test</a>',
            obj.old_path
        )
    test_link.short_description = 'Test URL'


# ── Chatbot Data & Conversations ──────────────────────────────────────────────

class ChatbotMessageInline(admin.TabularInline):
    model = ChatbotMessage
    extra = 0
    readonly_fields = ('sender_badge', 'message', 'timestamp')
    can_delete = True
    fields = ('sender_badge', 'message', 'timestamp')

    def sender_badge(self, obj):
        if obj.sender == 'user':
            return format_html('<span style="display:inline-block;padding:2px 8px;border-radius:10px;background:#2271b1;color:#fff;font-weight:600;font-size:11px;">👤 Visitor</span>')
        elif obj.sender == 'bot':
            return format_html('<span style="display:inline-block;padding:2px 8px;border-radius:10px;background:#646970;color:#fff;font-weight:600;font-size:11px;">🤖 AI Bot</span>')
        return format_html('<span style="display:inline-block;padding:2px 8px;border-radius:10px;background:#00a32a;color:#fff;font-weight:600;font-size:11px;">🎧 Staff</span>')
    sender_badge.short_description = 'Sender'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ('session_badge', 'visitor_ident', 'status_badge', 'interest_badge', 'message_count', 'latest_user_message', 'page_url', 'updated_at')
    list_filter = ('status', 'service_interest', 'created_at')
    search_fields = ('session_id', 'user_name', 'user_email', 'user_phone', 'messages__message', 'page_url')
    readonly_fields = ('session_id', 'ip_address', 'user_agent', 'page_url', 'created_at', 'updated_at', 'chat_transcript_view')
    actions = [export_as_csv_action('Export selected conversations to CSV'), 'mark_as_lead', 'mark_as_resolved']
    inlines = [ChatbotMessageInline]
    fieldsets = (
        ('Conversation Overview', {
            'fields': ('session_id', 'status', 'service_interest', 'admin_notes')
        }),
        ('Visitor Contact Details', {
            'fields': ('user_name', 'user_email', 'user_phone')
        }),
        ('Technical & Telemetry Data', {
            'classes': ('collapse',),
            'fields': ('page_url', 'ip_address', 'user_agent', 'created_at', 'updated_at')
        }),
        ('Full Chat Transcript', {
            'fields': ('chat_transcript_view',)
        }),
    )

    def session_badge(self, obj):
        short = obj.session_id[:12] + '...' if len(obj.session_id) > 12 else obj.session_id
        return format_html(
            '<span style="font-family:monospace;font-size:11px;font-weight:700;color:#1d2327;background:#f0f0f1;padding:2px 6px;border-radius:3px;">💬 {}</span>',
            short
        )
    session_badge.short_description = 'Session'

    def visitor_ident(self, obj):
        name = obj.user_name or 'Anonymous Visitor'
        parts = [format_html('<strong>{}</strong>', name)]
        if obj.user_email:
            parts.append(format_html('<br><a href="mailto:{}" style="font-size:11px;color:#2271b1;">{}</a>', obj.user_email, obj.user_email))
        if obj.user_phone:
            parts.append(format_html('<br><span style="font-size:11px;color:#646970;">📞 {}</span>', obj.user_phone))
        from django.utils.safestring import mark_safe
        return mark_safe(''.join(parts))
    visitor_ident.short_description = 'Visitor / Lead'

    def status_badge(self, obj):
        colors = {
            'lead': ('#d63638', '🎯 Lead Captured'),
            'active': ('#2271b1', '💬 Active Chat'),
            'resolved': ('#00a32a', '✅ Resolved'),
            'archived': ('#646970', '📁 Archived'),
        }
        bg, label = colors.get(obj.status, ('#646970', obj.status.title()))
        return format_html(
            '<span style="display:inline-block;padding:2px 8px;border-radius:10px;background:{};color:#fff;font-weight:600;font-size:11px;">{}</span>',
            bg, label
        )
    status_badge.short_description = 'Status'

    def interest_badge(self, obj):
        if not obj.service_interest:
            return '—'
        return format_html(
            '<span style="display:inline-block;padding:1px 6px;border-radius:4px;background:#e5f5fa;color:#0071a1;font-size:11px;font-weight:600;">{}</span>',
            obj.service_interest
        )
    interest_badge.short_description = 'Interest'

    def message_count(self, obj):
        count = obj.messages.count()
        return format_html('<strong>{}</strong> msgs', count)
    message_count.short_description = 'Messages'

    def latest_user_message(self, obj):
        last = obj.messages.filter(sender='user').last()
        if not last:
            last = obj.messages.last()
        if not last:
            return '—'
        snippet = (last.message[:65] + '...') if len(last.message) > 65 else last.message
        return format_html('<span style="color:#50575e;font-size:12px;">{}</span>', snippet)
    latest_user_message.short_description = 'Latest Message'

    def chat_transcript_view(self, obj):
        if not obj or not obj.id:
            return 'No transcript available.'
        msgs = obj.messages.all().order_by('timestamp')
        if not msgs:
            return 'No messages in this conversation yet.'
        html_out = ['<div style="max-height:450px;overflow-y:auto;padding:16px;background:#f6f7f7;border:1px solid #dcdcde;border-radius:6px;display:flex;flex-direction:column;gap:12px;">']
        for m in msgs:
            time_str = m.timestamp.strftime('%H:%M:%S')
            if m.sender == 'user':
                html_out.append(
                    f'<div style="align-self:flex-end;max-width:75%;background:#2271b1;color:#ffffff;padding:10px 14px;border-radius:12px 12px 2px 12px;box-shadow:0 1px 2px rgba(0,0,0,0.1);">'
                    f'<div style="font-size:11px;opacity:0.8;margin-bottom:3px;">👤 Visitor &middot; {time_str}</div>'
                    f'<div style="font-size:13px;white-space:pre-wrap;">{m.message}</div>'
                    f'</div>'
                )
            else:
                html_out.append(
                    f'<div style="align-self:flex-start;max-width:75%;background:#ffffff;color:#1d2327;border:1px solid #c3c4c7;padding:10px 14px;border-radius:12px 12px 12px 2px;box-shadow:0 1px 2px rgba(0,0,0,0.05);">'
                    f'<div style="font-size:11px;color:#646970;margin-bottom:3px;font-weight:600;">🤖 ProjectsHub AI &middot; {time_str}</div>'
                    f'<div style="font-size:13px;white-space:pre-wrap;">{m.message}</div>'
                    f'</div>'
                )
        html_out.append('</div>')
        return format_html(''.join(html_out))
    chat_transcript_view.short_description = 'Live Interactive Chat Viewer'

    def mark_as_lead(self, request, queryset):
        count = queryset.update(status='lead')
        self.message_user(request, f"{count} conversation(s) marked as Lead Captured 🎯.")
    mark_as_lead.short_description = "Mark selected as Lead Captured 🎯"

    def mark_as_resolved(self, request, queryset):
        count = queryset.update(status='resolved')
        self.message_user(request, f"{count} conversation(s) marked as Resolved ✅.")
    mark_as_resolved.short_description = "Mark selected as Resolved / Completed"


@admin.register(ChatbotMessage)
class ChatbotMessageAdmin(admin.ModelAdmin):
    list_display = ('sender_badge', 'message_snippet', 'conversation_link', 'timestamp')
    list_filter = ('sender', 'timestamp')
    search_fields = ('message', 'conversation__session_id', 'conversation__user_name', 'conversation__user_email')
    ordering = ('-timestamp',)

    def sender_badge(self, obj):
        if obj.sender == 'user':
            return format_html('<span style="display:inline-block;padding:2px 8px;border-radius:10px;background:#2271b1;color:#fff;font-weight:600;font-size:11px;">👤 Visitor</span>')
        elif obj.sender == 'bot':
            return format_html('<span style="display:inline-block;padding:2px 8px;border-radius:10px;background:#646970;color:#fff;font-weight:600;font-size:11px;">🤖 AI Bot</span>')
        return format_html('<span style="display:inline-block;padding:2px 8px;border-radius:10px;background:#00a32a;color:#fff;font-weight:600;font-size:11px;">🎧 Staff</span>')
    sender_badge.short_description = 'Sender'

    def message_snippet(self, obj):
        snippet = (obj.message[:80] + '...') if len(obj.message) > 80 else obj.message
        return snippet
    message_snippet.short_description = 'Message Content'

    def conversation_link(self, obj):
        return format_html(
            '<a href="/admin/core/chatbotconversation/{}/change/">Session {}</a>',
            obj.conversation.id,
            obj.conversation.session_id[:8]
        )
    conversation_link.short_description = 'Conversation'


# ── User Management & Permissions ─────────────────────────────────────────────

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('user_badge', 'email', 'role_badge', 'groups_summary', 'permissions_badge', 'is_active', 'last_login')
    list_filter = ('is_superuser', 'is_staff', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-is_superuser', '-is_staff', 'username')

    def user_badge(self, obj):
        full = obj.get_full_name()
        name_str = f" <span style='color:#646970;font-size:12px;'>({full})</span>" if full else ""
        return format_html(
            '<div style="display:flex;align-items:center;gap:8px;">'
            '<span style="display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:50%;background:#2271b1;color:#fff;font-weight:700;font-size:11px;">{}</span>'
            '<strong>{}</strong>{}'
            '</div>',
            obj.username[:2].upper(),
            obj.username,
            format_html(name_str)
        )
    user_badge.short_description = 'User (Username)'

    def role_badge(self, obj):
        if obj.is_superuser:
            return format_html('<span style="display:inline-block;padding:3px 8px;border-radius:10px;background:#1d2327;color:#f0b849;font-weight:700;font-size:11px;">👑 Administrator</span>')
        elif obj.is_staff:
            return format_html('<span style="display:inline-block;padding:3px 8px;border-radius:10px;background:#2271b1;color:#fff;font-weight:600;font-size:11px;">🛡️ Staff Manager</span>')
        return format_html('<span style="display:inline-block;padding:3px 8px;border-radius:10px;background:#f0f0f1;color:#50575e;font-size:11px;">👤 Standard User</span>')
    role_badge.short_description = 'System Role'

    def groups_summary(self, obj):
        groups = [g.name for g in obj.groups.all()]
        if not groups:
            return format_html('<span style="color:#8c8f94;font-style:italic;">None</span>')
        return format_html(' '.join([
            f'<span style="display:inline-block;padding:2px 6px;border-radius:3px;background:#e5f5fa;color:#0071a1;font-size:11px;font-weight:600;">🏷️ {g}</span>'
            for g in groups
        ]))
    groups_summary.short_description = 'Assigned Groups / Roles'

    def permissions_badge(self, obj):
        if obj.is_superuser:
            return format_html('<strong style="color:#00a32a;font-size:11px;">⚡ All Capabilities (Superuser)</strong>')
        perms = obj.get_all_permissions()
        if not perms:
            return format_html('<span style="color:#8c8f94;font-size:11px;">No Assigned Permissions</span>')
        return format_html(
            '<span style="display:inline-block;padding:2px 7px;border-radius:10px;background:#e7f5ea;color:#00a32a;font-weight:600;font-size:11px;">🔑 {} Permissions</span>',
            len(perms)
        )
    permissions_badge.short_description = 'Effective Permissions'


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_type', 'codename', 'assigned_groups_count', 'assigned_users_count')
    list_filter = ('content_type__app_label', 'content_type')
    search_fields = ('name', 'codename', 'content_type__model', 'content_type__app_label')
    ordering = ('content_type__app_label', 'content_type__model', 'codename')

    def assigned_groups_count(self, obj):
        count = obj.group_set.count()
        return format_html('<strong>{}</strong> groups', count) if count else '—'
    assigned_groups_count.short_description = 'Assigned Groups'

    def assigned_users_count(self, obj):
        count = obj.user_set.count()
        return format_html('<strong>{}</strong> users', count) if count else '—'
    assigned_users_count.short_description = 'Direct Users'


# ── Operational Manual & Guide Notes ───────────────────────────────────────────

@admin.register(AdminGuideNote)
class AdminGuideNoteAdmin(admin.ModelAdmin):
    list_display = ('title_with_pin', 'category_badge', 'action_shortcut', 'is_completed', 'is_pinned', 'order', 'updated_at')
    list_editable = ('is_completed', 'is_pinned', 'order')
    list_filter = ('category', 'is_pinned', 'is_completed')
    search_fields = ('title', 'content')
    actions = ['mark_completed', 'mark_uncompleted', 'mark_pinned', 'mark_unpinned', export_as_csv_action('Export guide notes to CSV')]

    fieldsets = (
        ('Note & Documentation', {
            'fields': ('title', 'category', 'content', 'order')
        }),
        ('Action Shortcut & Checklist', {
            'fields': ('action_url', 'action_label', 'is_completed', 'is_pinned'),
            'description': 'Provide a 1-click admin shortcut for this operational instruction.'
        }),
    )

    def title_with_pin(self, obj):
        pin = '📌 ' if obj.is_pinned else ''
        status = format_html('<s>{}</s>', obj.title) if obj.is_completed else obj.title
        return format_html('{}{}', pin, status)
    title_with_pin.short_description = 'Note / Instruction'

    def category_badge(self, obj):
        colors = {
            'general': '#3b82f6',
            'branding': '#6366f1',
            'navigation': '#8b5cf6',
            'projects': '#0284c7',
            'tools': '#059669',
            'services': '#0891b2',
            'workshops': '#d97706',
            'blog': '#dc2626',
            'crm': '#ec4899',
            'seo': '#475569',
            'checklist': '#16a34a',
        }
        c = colors.get(obj.category, '#64748b')
        return format_html(
            '<span style="display:inline-block;padding:2px 8px;border-radius:12px;background:{}15;color:{};border:1px solid {}30;font-size:11px;font-weight:600;">{}</span>',
            c, c, c, obj.get_category_display()
        )
    category_badge.short_description = 'Category'

    def action_shortcut(self, obj):
        if obj.action_url:
            label = obj.action_label or 'Open ↗'
            return format_html(
                '<a href="{}" class="button button-small" style="text-decoration:none;font-size:11px;padding:2px 8px;border-radius:4px;">{}</a>',
                obj.action_url, label
            )
        return '—'
    action_shortcut.short_description = 'Action Shortcut'

    def mark_completed(self, request, queryset):
        queryset.update(is_completed=True)
    mark_completed.short_description = "Mark selected as completed"

    def mark_uncompleted(self, request, queryset):
        queryset.update(is_completed=False)
    mark_uncompleted.short_description = "Mark selected as uncompleted"

    def mark_pinned(self, request, queryset):
        queryset.update(is_pinned=True)
    mark_pinned.short_description = "Pin selected notes"

    def mark_unpinned(self, request, queryset):
        queryset.update(is_pinned=False)
    mark_unpinned.short_description = "Unpin selected notes"



