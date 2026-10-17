"""
Smoke tests for admin URLs reported as broken.
Verifies that all admin assets and ToolCategory URLs return 200 for staff users.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from core.models import FAQ, Page

User = get_user_model()


class AdminURLSmokeTests(TestCase):
    """Test that all reported admin URLs load successfully for staff users."""

    def setUp(self):
        """Create a staff user and authenticate."""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='teststaff',
            email='staff@test.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.client.login(username='teststaff', password='testpass123')

    def test_admin_assets_base_url_returns_200(self):
        """Test that /admin/assets/ loads successfully."""
        response = self.client.get('/admin/assets/')
        self.assertEqual(response.status_code, 200, 
                         f"Expected 200, got {response.status_code} for /admin/assets/")

    def test_admin_assets_filter_unused_returns_200(self):
        """Test that /admin/assets/?filter=unused loads successfully."""
        response = self.client.get('/admin/assets/?filter=unused')
        self.assertEqual(response.status_code, 200,
                         f"Expected 200, got {response.status_code} for /admin/assets/?filter=unused")

    def test_admin_assets_sort_size_desc_returns_200(self):
        """Test that /admin/assets/?sort=size_desc loads successfully."""
        response = self.client.get('/admin/assets/?sort=size_desc')
        self.assertEqual(response.status_code, 200,
                         f"Expected 200, got {response.status_code} for /admin/assets/?sort=size_desc")

    def test_admin_core_toolcategory_returns_200(self):
        """Test that /admin/core/toolcategory/ loads successfully."""
        response = self.client.get('/admin/core/toolcategory/')
        self.assertEqual(response.status_code, 200,
                         f"Expected 200, got {response.status_code} for /admin/core/toolcategory/")

    def test_admin_dashboard_uses_django_app_index_and_actions(self):
        response = self.client.get('/admin/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django administration')
        self.assertContains(response, 'Applications')
        self.assertContains(response, 'Quick actions')
        self.assertContains(response, 'Add a page')
        self.assertContains(response, 'dashboard-app-list')
        self.assertContains(response, 'Search admin sections')
        self.assertContains(response, '<details class="dashboard-app">')
        self.assertContains(response, 'dashboard-app-count')
        self.assertNotContains(response, 'welcome-panel')
        self.assertNotContains(response, 'At a Glance')

    def test_admin_dashboard_hides_actions_without_model_permissions(self):
        staff_user = User.objects.create_user(
            username='limitedstaff',
            email='limited@test.com',
            password='testpass123',
            is_staff=True,
        )
        self.client.force_login(staff_user)

        response = self.client.get('/admin/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You do not have permission to view or edit any records.')
        self.assertNotContains(response, 'Add a page')
        self.assertNotContains(response, 'Add a project')

    def test_shared_admin_navigation_is_searchable_and_permission_aware(self):
        response = self.client.get('/admin/core/page/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Find a section')
        self.assertContains(response, 'admin-nav-app')
        self.assertContains(response, 'href="/admin/core/page/"')
        self.assertContains(response, 'aria-label="Add Pages"')
        self.assertContains(response, 'Close navigation menu')
        # Models are grouped into WordPress-style sections, not one flat "Core" list.
        self.assertContains(response, 'title="Pages"')
        self.assertContains(response, 'title="Appearance"')
        self.assertContains(response, 'Workspace tools')
        self.assertNotContains(response, 'class="admin-nav-info"')
        self.assertNotContains(response, 'aria-label="About Pages"')
        self.assertNotContains(response, 'Manage Pages records here.')
        # The legacy hardcoded (non-permission-aware) "Plugins" menu must stay gone.
        self.assertNotContains(response, 'Plugins')

    def test_faq_admin_has_a_clear_add_and_homepage_management_workflow(self):
        FAQ.objects.create(question='Can I add FAQs?', answer='Add answers directly in the admin.')
        response = self.client.get('/admin/core/faq/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manage homepage FAQs')
        self.assertContains(response, 'href="/admin/core/faq/add/"')
        self.assertContains(response, 'Only published FAQs appear on the homepage.')
        self.assertContains(response, 'Can I add FAQs?')
        self.assertContains(response, 'Add answers directly in the admin.')

    def test_quick_edit_uses_a_valid_table_template(self):
        response = self.client.get('/admin/auth/user/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<template id="wp-quick-edit-template">')
        self.assertContains(response, '<tr class="inline-edit-row quick-edit-row"')

    def test_pages_list_displays_pages_and_filters_by_page_status(self):
        initial_counts = {
            status: Page.objects.filter(status=status).count()
            for status, _ in Page.STATUS_CHOICES
        }
        Page.objects.create(title='Published page', slug='published-page', status='published')
        Page.objects.create(title='Draft page', slug='draft-page', status='draft')
        Page.objects.create(title='Trashed page', slug='trashed-page', status='trash')

        response = self.client.get('/admin/core/page/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published page')
        self.assertContains(response, 'Draft page')
        self.assertContains(response, 'Trashed page')
        self.assertContains(response, f'All <span class="count">({sum(initial_counts.values()) + 3})</span>')
        self.assertContains(response, '?status__exact=published')
        self.assertContains(response, f'Published <span class="count">({initial_counts["published"] + 1})</span>')
        self.assertContains(response, '?status__exact=draft')
        self.assertContains(response, '?status__exact=trash')

        response = self.client.get('/admin/core/page/?status__exact=draft')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Draft page')
        self.assertNotContains(response, 'Published page')
        self.assertNotContains(response, 'Trashed page')

    def test_seeded_site_pages_show_routes_and_use_cms_body_when_configured(self):
        page = Page.objects.get(site_path='/contact/')
        self.assertEqual(page.get_absolute_url(), '/contact/')

        default_response = self.client.get('/contact/')
        self.assertEqual(default_response.status_code, 200)
        self.assertContains(default_response, "Let's Build Something")

        page.content = '<p>Editable contact page body</p>'
        page.save()

        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editable contact page body')
        self.assertContains(response, '/contact/')
        self.assertContains(response, 'id="contactForm"')
        self.assertContains(response, 'id="contactCaptcha"')

        post_response = self.client.post('/contact/', {})
        self.assertEqual(post_response.status_code, 400)
        self.assertJSONEqual(post_response.content, {'success': False, 'errors': {
            'name': 'Full name is required.',
            'email': 'Valid email is required.',
            'message': 'Message is required.',
            'catch_code': 'Catch code (security verification) is required.',
        }})

    def test_seeded_site_routes_render_their_existing_pages(self):
        expected_paths = {
            '/',
            '/projects/',
            '/workshop/',
            '/case-studies/',
            '/tools/',
            '/ai-roadmap/',
            '/services/ai-development/',
            '/services/ai-automation/',
            '/services/ai-integration/',
            '/industries/',
            '/blog/',
            '/contact/',
            '/terms/',
            '/refund/',
            '/privacy/',
            '/sitemap/',
        }
        self.assertSetEqual(
            set(Page.objects.filter(site_path__isnull=False).values_list('site_path', flat=True)),
            expected_paths,
        )

        for site_path in sorted(expected_paths):
            with self.subTest(site_path=site_path):
                response = self.client.get(site_path)
                self.assertEqual(response.status_code, 200)

    def test_pages_sidebar_does_not_show_a_fake_default_count(self):
        cache.clear()
        response = self.client.get('/admin/core/page/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['model_counts']['page'],
            Page.objects.filter(site_path__isnull=False).count(),
        )
        self.assertNotContains(response, 'All Pages (8)')

    def test_page_editor_exposes_status_and_draft_preview_controls(self):
        page = Page.objects.create(
            title='Draft page',
            slug='custom-page-url',
            status='draft',
        )

        response = self.client.get(f'/admin/core/page/{page.pk}/change/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="id_status"')
        self.assertContains(response, 'Save as Draft')
        self.assertContains(response, 'Move to Trash')
        self.assertContains(response, 'custom-page-url/?preview=true')
        self.assertRegex(
            response.content.decode(),
            r'css/page-editor-layout(?:\.[a-f0-9]+)?\.css',
        )

    def test_page_quick_edit_preserves_custom_slug_and_validates_status(self):
        page = Page.objects.create(
            title='Existing title',
            slug='custom-page-url',
            status='draft',
        )
        data = {
            'app_label': 'core',
            'model_name': 'page',
            'object_id': page.pk,
            'title': 'Updated title',
            'slug': 'custom-page-url',
            'status': 'draft',
        }

        response = self.client.post('/admin/api/quick-edit/', data)

        self.assertEqual(response.status_code, 200)
        page.refresh_from_db()
        self.assertEqual(page.title, 'Updated title')
        self.assertEqual(page.slug, 'custom-page-url')
        self.assertEqual(page.status, 'draft')

        data['status'] = 'not-a-page-status'
        response = self.client.post('/admin/api/quick-edit/', data)
        self.assertEqual(response.status_code, 400)
