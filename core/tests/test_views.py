from django.test import TestCase, Client
from django.urls import reverse
from core.models import Project, ProjectCategory, Technology


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

    def test_project_detail_by_slug(self):
        res = self.client.get(reverse('project_detail_slug', args=[self.project.slug]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Smart Fraud Detection")

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

