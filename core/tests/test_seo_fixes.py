"""Regression tests for the October 2026 SEO / security audit fixes."""
import json
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from core.models import BlogPost, Project, ProjectCategory, Redirect, SEOData, WorkshopCard, WorkshopDay
from core.seo import clean_description, safe_json_ld

CANON = 'https://projectshub.co.in'


@override_settings(CANONICAL_SITE_URL=CANON, ALLOWED_HOSTS=['*'])
class CanonicalDomainTests(TestCase):
    def setUp(self):
        cat = ProjectCategory.objects.create(name='ML', slug='ml', icon='ml')
        self.project = Project.objects.create(
            title='Fraud Detector', slug='fraud-detector', category='ml', category_ref=cat,
            description='**Bold** fraud detection with *PyTorch*.', price=0, is_active=True,
        )

    def test_platform_host_does_not_leak_into_canonical_or_sitemap(self):
        host = 'projectshub-production.up.railway.app'
        for url in ('/projects/', '/robots.txt', '/sitemap.xml', self.project.get_absolute_url()):
            res = self.client.get(url, HTTP_HOST=host)
            self.assertEqual(res.status_code, 200, url)
            self.assertNotIn(host, res.content.decode(), url)
            self.assertEqual(res['X-Robots-Tag'], 'noindex, nofollow')

    def test_primary_host_is_indexable(self):
        res = self.client.get('/projects/', HTTP_HOST='projectshub.co.in', secure=True)
        self.assertFalse(res.has_header('X-Robots-Tag'))
        self.assertContains(res, f'rel="canonical" href="{CANON}/projects/"')

    def test_numeric_project_url_redirects_to_slug(self):
        res = self.client.get(f'/projects/{self.project.pk}/?ref=x')
        self.assertEqual(res.status_code, 301)
        self.assertEqual(res['Location'], '/projects/fraud-detector/?ref=x')

    def test_project_canonical_matches_sitemap_and_description_is_plain(self):
        body = self.client.get('/projects/fraud-detector/').content.decode()
        self.assertIn(f'rel="canonical" href="{CANON}/projects/fraud-detector/"', body)
        desc = re.search(r'<meta name="description"\s+content="(.*?)"', body, re.S).group(1)
        self.assertNotIn('*', desc)
        self.assertIn(f'{CANON}/projects/fraud-detector/', self.client.get('/sitemap.xml').content.decode())

    def test_homepage_canonical_has_no_whitespace(self):
        body = self.client.get('/').content.decode()
        self.assertIn(f'rel="canonical" href="{CANON}/"', body)


@override_settings(CANONICAL_SITE_URL=CANON)
class SitemapTests(TestCase):
    def test_excludes_redirected_and_noindex_paths_and_includes_workshops(self):
        Redirect.objects.create(old_path='/industries/', new_path='/services/ai-development/')
        SEOData.objects.create(path='/refund/', meta_title='x', meta_description='y', is_indexable=False)
        w = WorkshopCard.objects.create(title='Bootcamp', is_active=True)
        WorkshopDay.objects.create(workshop=w, day_number=1, title='Day 1')
        xml = self.client.get('/sitemap.xml').content.decode()
        self.assertNotIn(f'{CANON}/industries/<', xml)
        self.assertNotIn(f'{CANON}/refund/<', xml)
        self.assertIn(f'{CANON}/workshop/{w.pk}/<', xml)
        self.assertIn(f'{CANON}/workshop/{w.pk}/day/1/<', xml)
        locs = re.findall(r'<loc>(.*?)</loc>', xml)
        self.assertEqual(len(locs), len(set(locs)), 'sitemap contains duplicate URLs')


class JsonLdSafetyTests(TestCase):
    def test_script_breakout_is_escaped(self):
        out = safe_json_ld({'headline': '</script><script>alert(1)</script>'})
        self.assertNotIn('</script>', out)
        self.assertEqual(json.loads(out)['headline'], '</script><script>alert(1)</script>')

    def test_blog_json_ld_is_valid_and_escaped(self):
        BlogPost.objects.create(title='Evil </script><b>x', slug='t', is_active=True, is_published=True)
        body = self.client.get('/blog/t/').content.decode()
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S)
        posting = [json.loads(b) for b in blocks if '"BlogPosting"' in b][0]
        self.assertEqual(posting['headline'], 'Evil </script><b>x')
        self.assertTrue(posting.get('datePublished'))

    def test_clean_description(self):
        self.assertEqual(clean_description('**Hi** <b>there</b>\n\n  `x`'), 'Hi there x')
        self.assertLessEqual(len(clean_description('word ' * 100)), 156)


class RedirectValidationTests(TestCase):
    def test_rejects_open_redirect_self_loop_chain_and_loop(self):
        with self.assertRaises(ValidationError):
            Redirect(old_path='/a/', new_path='https://evil.example/').full_clean()
        with self.assertRaises(ValidationError):
            Redirect(old_path='/a/', new_path='//evil.example/').full_clean()
        with self.assertRaises(ValidationError):
            Redirect(old_path='/a/', new_path='/a').full_clean()
        Redirect.objects.create(old_path='/b/', new_path='/c/')
        with self.assertRaises(ValidationError):  # chain a -> b -> c
            Redirect(old_path='/a/', new_path='/b/').full_clean()
        with self.assertRaises(ValidationError):  # loop c -> b -> c
            Redirect(old_path='/c/', new_path='/b/').full_clean()
        with self.assertRaises(ValidationError):  # incoming chain: x -> c -> d? (b -> c exists)
            Redirect(old_path='/c/', new_path='/d/').full_clean()
        Redirect(old_path='/old/', new_path='https://projectshub.co.in/projects/').full_clean()


class QuickEditPermissionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.victim = User.objects.create_superuser('boss', 'boss@example.com', 'pw-Strong-123!')
        self.staff = User.objects.create_user('editor', 'ed@example.com', 'pw-Strong-123!', is_staff=True)
        self.client.force_login(self.staff)

    def test_cannot_touch_auth_users(self):
        res = self.client.post('/admin/api/quick-edit/', {
            'app_label': 'auth', 'model_name': 'user', 'object_id': self.victim.pk, 'status': 'draft'})
        self.assertEqual(res.status_code, 403)
        self.victim.refresh_from_db()
        self.assertTrue(self.victim.is_active)

    def test_requires_change_permission(self):
        p = Project.objects.create(title='P', slug='p', category='ml', price=0, is_active=True)
        data = {'app_label': 'core', 'model_name': 'project', 'object_id': p.pk, 'title': 'New'}
        self.assertEqual(self.client.post('/admin/api/quick-edit/', data).status_code, 403)
        self.staff.user_permissions.add(Permission.objects.get(codename='change_project'))
        self.assertEqual(self.client.post('/admin/api/quick-edit/', data).status_code, 200)


class ClientIpAndLeadRateTests(TestCase):
    def setUp(self):
        cache.clear()

    @override_settings(TRUSTED_PROXY_COUNT=1)
    def test_spoofed_forwarded_for_does_not_bypass_lead_limit(self):
        for i in range(5):
            res = self.client.post('/api/chatbot/lead/', {'session_id': f's{i}', 'email': 'a@b.co'},
                                   HTTP_X_FORWARDED_FOR=f'10.0.0.{i}, 203.0.113.9')
            self.assertEqual(res.status_code, 200)
        res = self.client.post('/api/chatbot/lead/', {'session_id': 's9', 'email': 'a@b.co'},
                               HTTP_X_FORWARDED_FOR='1.2.3.4, 203.0.113.9')
        self.assertEqual(res.status_code, 429)
