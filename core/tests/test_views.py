from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import (
    ChatbotConversation,
    ContactInquiry,
    BlogPost,
    Page,
    Project,
    ProjectCategory,
    Technology,
    NavigationItem,
)
from core.seo import get_seo_for_request


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = ProjectCategory.objects.create(
            name="Machine Learning",
            slug="ml",
            icon="ml"
        )
        self.project = Project.objects.create(
            title="Smart Fraud Detection",
            slug="smart-fraud-detection",
            category="ml",
            category_ref=self.category,
            description="Real-time financial fraud detection using PyTorch.",
            price=0,
            is_active=True,
            show_on_index=True
        )

    def test_index_view(self):
        res = self.client.get(reverse('index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "ProjectsHub")
        self.assertContains(res, "Smart Fraud Detection")

    def test_admin_navigation_items_render_in_mobile_menu_with_icons(self):
        NavigationItem.objects.create(
            title="Featured Research",
            url="/projects/?category=ml",
            group="our_work",
            icon_svg="🧪",
            is_active=True,
            open_in_new_tab=True,
        )

        response = self.client.get(reverse('index'))

        self.assertContains(response, '🧪')
        self.assertContains(response, 'Featured Research')
        self.assertContains(response, 'href="/projects/?category=ml"')
        self.assertContains(response, 'target="_blank" rel="noopener noreferrer"')

    def test_projects_view(self):
        res = self.client.get(reverse('projects'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Smart Fraud Detection")

    def test_projects_filter_ajax(self):
        res = self.client.get(reverse('projects'), {'category': 'ml'}, HTTP_HX_REQUEST='true')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Smart Fraud Detection")

    def test_project_detail_by_id(self):
        res = self.client.get(reverse('project_detail', args=[self.project.id]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Smart Fraud Detection")
        self.assertContains(res, '"applicationCategory": "Machine Learning"')
        self.assertNotContains(res, '"aggregateRating"')
        self.assertNotContains(res, '"price": "Free"')

    def test_project_detail_by_slug(self):
        res = self.client.get(reverse('project_detail_slug', args=[self.project.slug]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Smart Fraud Detection")

    def test_model_structured_data_uses_recorded_project_and_article_facts(self):
        request_factory = RequestFactory()
        project_seo = get_seo_for_request(
            request_factory.get('/projects/smart-fraud-detection/'),
            {'project': self.project},
        )
        software_schema = next(
            schema for schema in project_seo['schemas']
            if schema.get('@type') == 'SoftwareApplication'
        )
        self.assertEqual(software_schema['applicationCategory'], 'Machine Learning')
        self.assertNotIn('aggregateRating', software_schema)
        self.assertNotIn('offers', software_schema)

        post = BlogPost.objects.create(
            title='Fact-checked AI guide',
            slug='fact-checked-ai-guide',
            author_name='ProjectsHub Editorial Team',
            is_active=True,
            is_published=True,
        )
        post_seo = get_seo_for_request(
            request_factory.get('/blog/fact-checked-ai-guide/'),
            {'post': post},
        )
        article_schema = next(
            schema for schema in post_seo['schemas']
            if schema.get('@type') == 'BlogPosting'
        )
        self.assertEqual(article_schema['author']['name'], 'ProjectsHub Editorial Team')
        self.assertEqual(article_schema['datePublished'], post.published_at.isoformat())

    def test_blog_detail_only_exposes_published_posts_and_links_related_resources(self):
        published_post = BlogPost.objects.create(
            title='Production AI API guide',
            slug='production-ai-api-guide',
            category='engineering',
            is_active=True,
            is_published=True,
        )
        BlogPost.objects.create(
            title='Unpublished API draft',
            slug='unpublished-api-draft',
            category='engineering',
            is_active=True,
            is_published=False,
        )

        response = self.client.get(reverse('blog_detail', args=[published_post.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Browse AI and machine-learning projects')
        self.assertContains(response, 'Explore developer tools')
        self.assertContains(response, 'Follow the AI engineering roadmap')
        self.assertContains(response, '<title>Production AI API guide | ProjectsHub Blog</title>')
        self.assertContains(response, '<meta name="description"')
        self.assertContains(response, '"@type": "BlogPosting"')
        self.assertContains(response, '"image": "http://testserver/static/image/ai-project-ideas-students.webp"')
        self.assertNotContains(response, 'Unpublished API draft')
        self.assertEqual(response.context['seo']['canonical_url'], 'http://testserver/blog/production-ai-api-guide/')

        api_response = self.client.get(reverse('api_blog'))
        api_slugs = {post['slug'] for post in api_response.json()['posts']}
        self.assertIn(published_post.slug, api_slugs)
        self.assertNotIn('unpublished-api-draft', api_slugs)

    def test_unpublished_blog_post_is_not_accessible_by_direct_url(self):
        post = BlogPost.objects.create(
            title='Unpublished API draft',
            slug='unpublished-api-draft',
            is_active=True,
            is_published=False,
        )

        response = self.client.get(reverse('blog_detail', args=[post.slug]))

        self.assertEqual(response.status_code, 404)

    def test_tools_view(self):
        res = self.client.get(reverse('tools'))
        self.assertEqual(res.status_code, 200)

    def test_case_studies_view(self):
        res = self.client.get(reverse('case_studies'))
        self.assertEqual(res.status_code, 200)

    def test_sitemap_xml(self):
        res = self.client.get('/sitemap.xml')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/xml')
        self.assertContains(res, 'http://testserver/projects/')

        # Test custom domain via host header
        res_custom = self.client.get('/sitemap.xml', HTTP_HOST='projectshub.co.in', secure=True)
        self.assertContains(res_custom, 'https://projectshub.co.in/projects/')

    def test_sitemap_only_lists_active_projects_and_published_posts(self):
        import xml.etree.ElementTree as ET

        BlogPost.objects.create(
            title='Published AI guide',
            slug='published-ai-guide',
            is_active=True,
            is_published=True,
        )
        BlogPost.objects.create(
            title='Draft AI guide',
            slug='draft-ai-guide',
            is_active=True,
            is_published=False,
        )
        Project.objects.create(
            title='Inactive project',
            slug='inactive-project',
            is_active=False,
        )
        Project.objects.create(
            title='Unpublished project',
            slug='unpublished-project',
            is_active=True,
            is_published=False,
        )
        published_page = Page.objects.create(
            title='About ProjectsHub',
            slug='about-projectshub',
            status='published',
        )
        Page.objects.create(
            title='Draft page',
            slug='draft-page',
            status='draft',
        )

        response = self.client.get(reverse('sitemap_xml'))
        root = ET.fromstring(response.content)
        locs = {
            element.text
            for element in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        }

        self.assertIn('http://testserver/projects/smart-fraud-detection/', locs)
        self.assertIn('http://testserver/blog/published-ai-guide/', locs)
        self.assertIn(f'http://testserver{published_page.get_absolute_url()}', locs)
        self.assertNotIn('http://testserver/blog/draft-ai-guide/', locs)
        self.assertNotIn('http://testserver/projects/inactive-project/', locs)
        self.assertNotIn('http://testserver/projects/unpublished-project/', locs)
        self.assertNotIn('http://testserver/draft-page/', locs)

    def test_404_is_noindex_and_has_no_canonical_url(self):
        response = self.client.get('/page-that-does-not-exist/')

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'noindex, follow', status_code=404)
        self.assertNotContains(response, 'rel="canonical"', status_code=404)

    def test_llms_txt_lists_verified_public_sections(self):
        response = self.client.get(reverse('llms_txt'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('text/plain'))
        self.assertContains(response, 'http://testserver/projects/')
        self.assertContains(response, 'http://testserver/blog/')
        self.assertContains(response, 'source of truth for current content and offerings')

    def test_robots_txt(self):
        res = self.client.get('/robots.txt')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'text/plain')
        self.assertContains(res, 'User-agent: *')
        self.assertContains(res, 'Sitemap: http://testserver/sitemap.xml')

        # Test custom domain via host header
        res_custom = self.client.get('/robots.txt', HTTP_HOST='projectshub.co.in', secure=True)
        self.assertContains(res_custom, 'Sitemap: https://projectshub.co.in/sitemap.xml')

    def test_api_captcha(self):
        res = self.client.get(reverse('api_captcha'))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(data.get('token'))
        self.assertIn('<svg', data.get('svg', ''))

    def test_contact_submit_catch_code_required(self):
        import json
        res = self.client.post(reverse('contact_submit'), json.dumps({
            'full_name': 'Test User',
            'email': 'test@example.com',
            'message': 'Hello'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIn('catch_code', data.get('errors', {}))

    def test_contact_submit_with_valid_catch_code(self):
        import json
        from django.core import signing
        # Get captcha first
        c_res = self.client.get(reverse('api_captcha'))
        token = c_res.json()['token']
        code = signing.loads(token, salt='captcha-salt')

        res = self.client.post(reverse('contact_submit'), json.dumps({
            'full_name': 'Valid User',
            'email': 'user@example.com',
            'subject': 'Project Inquiry',
            'message': 'Valid message with catch code',
            'catch_code': code,
            'captcha_token': token
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('success'))

    def test_contact_page_get(self):
        res = self.client.get(reverse('contact'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'core/contact.html')
        self.assertContains(res, 'Send Us a Message')
        self.assertContains(res, 'contactForm')

    def test_contact_page_post_delegates(self):
        import json
        from django.core import signing
        c_res = self.client.get(reverse('api_captcha'))
        token = c_res.json()['token']
        code = signing.loads(token, salt='captcha-salt')

        res = self.client.post(reverse('contact'), json.dumps({
            'full_name': 'Direct Page User',
            'email': 'direct@example.com',
            'subject': 'Direct Inquiry',
            'message': 'Testing delegation on /contact/',
            'catch_code': code,
            'captcha_token': token
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('success'))


class ChatbotLeadEndpointTests(TestCase):
    def test_lead_endpoint_saves_chatbot_and_contact_records(self):
        import json

        response = self.client.post(
            reverse('api_chatbot_lead'),
            data=json.dumps({
                'session_id': 'lead-endpoint-test',
                'name': 'Lead Tester',
                'email': 'lead@example.com',
                'interest': 'AI development',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(
            ChatbotConversation.objects.get(session_id='lead-endpoint-test').status,
            'lead',
        )
        inquiry = ContactInquiry.objects.get(email='lead@example.com')
        self.assertEqual(inquiry.name, 'Lead Tester')
        self.assertEqual(inquiry.subject, 'Chatbot Lead: AI development')

    def test_lead_endpoint_rejects_non_post_method(self):
        response = self.client.get(reverse('api_chatbot_lead'))

        self.assertEqual(response.status_code, 405)


class NavigationItemAdminTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="navigation-admin",
            email="navigation-admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.admin_user)

    def test_admin_form_exposes_mobile_menu_groups_and_icon_field(self):
        response = self.client.get(reverse('admin:core_navigationitem_add'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Icon / Emoji")
        self.assertContains(response, "Mega Menu — Our Work")
        self.assertContains(response, "How We Help (Students)")
        self.assertContains(response, "How We Help (Businesses)")

    def test_menu_builder_adds_and_edits_mobile_item_icons(self):
        menu_url = reverse('admin_nav_menus')
        response = self.client.post(
            f'{menu_url}?menu=our_work',
            {
                'action': 'add_custom',
                'link_text': 'Research Projects',
                'url': '/projects/?category=research',
                'icon': '🧪',
            },
        )

        self.assertEqual(response.status_code, 302)
        item = NavigationItem.objects.get(title='Research Projects')
        self.assertEqual(item.group, 'our_work')
        self.assertEqual(item.icon_svg, '🧪')

        response = self.client.post(
            f'{menu_url}?menu=our_work',
            {
                'action': 'save_menu',
                'item_id[]': str(item.pk),
                f'title_{item.pk}': 'Featured Research',
                f'url_{item.pk}': '/projects/?category=research',
                f'badge_{item.pk}': 'NEW',
                f'icon_{item.pk}': '🔬',
            },
        )

        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.title, 'Featured Research')
        self.assertEqual(item.icon_svg, '🔬')
