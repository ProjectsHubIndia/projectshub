from django.test import TestCase, Client
from core.models import Redirect


class RedirectTests(TestCase):
    def setUp(self):
        self.client = Client()
        Redirect.objects.create(
            old_path="/old-portfolio/",
            new_path="/projects/",
            status_code=301,
            is_active=True
        )
        Redirect.objects.create(
            old_path="/free-ai-tools/",
            new_path="/tools/",
            status_code=302,
            is_active=True
        )

    def test_permanent_redirect(self):
        res = self.client.get('/old-portfolio/')
        self.assertEqual(res.status_code, 301)
        self.assertEqual(res.headers['Location'], '/projects/')

    def test_temporary_redirect(self):
        res = self.client.get('/free-ai-tools/')
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.headers['Location'], '/tools/')
