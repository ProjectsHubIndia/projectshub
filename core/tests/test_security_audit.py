import json
from unittest.mock import patch
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.core.cache import cache
from django.core import signing
from django.urls import reverse
from core.models import (
    ChatbotConversation, ChatbotMessage, Redirect
)
from core.admin import ChatbotConversationAdmin
from core.middleware import RedirectMiddleware
import projectshub.wsgi

User = get_user_model()


class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check_endpoint(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response['Content-Type'])
        data = response.json()
        self.assertEqual(data.get('status'), 'healthy')
        self.assertEqual(data.get('database'), 'connected')


class SuperuserAdminGuardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff_member', email='staff@example.com', password='password123', is_staff=True
        )
        self.superuser = User.objects.create_superuser(
            username='super_admin', email='admin@example.com', password='password123'
        )
        self.backup_endpoints = [
            reverse('admin_backup_download_db'),
            reverse('admin_backup_download_json'),
            reverse('admin_backup_sync_initial'),
            reverse('admin_backup_restore'),
            reverse('admin_asset_delete'),
        ]

    def test_unauthenticated_blocked_from_backups(self):
        for url in self.backup_endpoints:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 302)
            self.assertIn('/admin/login/', res.url)

    def test_staff_non_superuser_blocked_from_backups(self):
        self.client.force_login(self.staff_user)
        for url in self.backup_endpoints:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 302)
            self.assertIn('/admin/login/', res.url)

    def test_superuser_allowed_to_download_json_backup(self):
        self.client.force_login(self.superuser)
        res = self.client.get(reverse('admin_backup_download_json'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('application/json', res['Content-Type'])


class ChatbotSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_message_length_limit(self):
        long_msg = "A" * 1001
        res = self.client.post(
            '/api/chatbot/message/',
            data=json.dumps({
                'session_id': 'audit-session-len',
                'message': long_msg
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertFalse(data.get('success'))
        self.assertIn('Message exceeds maximum', data.get('error', ''))

    def test_rate_limiting_exceeded(self):
        for i in range(30):
            res = self.client.post(
                '/api/chatbot/message/',
                data=json.dumps({
                    'session_id': f'audit-session-rate-{i}',
                    'message': 'hello'
                }),
                content_type='application/json'
            )
            self.assertEqual(res.status_code, 200)

        res = self.client.post(
            '/api/chatbot/message/',
            data=json.dumps({
                'session_id': 'audit-session-rate-overflow',
                'message': 'hello again'
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 429)
        data = res.json()
        self.assertFalse(data.get('success'))
        self.assertIn('Rate limit exceeded', data.get('error', ''))


class CaptchaReplayProtectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_captcha_token_replay_blocked(self):
        answer = "A9X2"
        token = signing.dumps(answer, salt='captcha-salt')

        payload = {
            'name': 'Audit Tester',
            'email': 'tester@example.com',
            'subject': 'Test Subject',
            'message': 'Test message content for audit.',
            'catch_code': answer,
            'captcha_token': token,
        }

        # First attempt should succeed
        res1 = self.client.post(
            reverse('contact_submit'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res1.status_code, 200)
        self.assertTrue(res1.json().get('success'))

        # Second attempt with the identical token should be rejected
        res2 = self.client.post(
            reverse('contact_submit'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res2.status_code, 400)
        data2 = res2.json()
        self.assertFalse(data2.get('success'))
        self.assertIn('already been used', data2.get('errors', {}).get('catch_code', ''))


class XSSProtectionTests(TestCase):
    def test_admin_chat_transcript_escapes_xss(self):
        conv = ChatbotConversation.objects.create(session_id='xss-test-session')
        ChatbotMessage.objects.create(
            conversation=conv,
            sender='user',
            message='<script>alert("xss")</script><img src=x onerror=alert(1)>'
        )
        admin_instance = ChatbotConversationAdmin(ChatbotConversation, AdminSite())
        rendered_html = admin_instance.chat_transcript_view(conv)

        # Verify HTML entities are escaped
        self.assertIn('&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;', rendered_html)
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', rendered_html)
        self.assertNotIn('<script>alert("xss")</script>', rendered_html)


class OpenRedirectMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RedirectMiddleware(lambda r: None)

    def test_open_redirect_protocol_relative_blocked(self):
        Redirect.objects.create(
            old_path='/unsafe-redirect-1',
            new_path='//evil.com/phish',
            is_active=True
        )
        req = self.factory.get('/unsafe-redirect-1')
        res = self.middleware.process_request(req)
        self.assertIsNone(res)

    def test_open_redirect_external_domain_blocked(self):
        Redirect.objects.create(
            old_path='/unsafe-redirect-2',
            new_path='https://malicious-site.com',
            is_active=True
        )
        req = self.factory.get('/unsafe-redirect-2')
        res = self.middleware.process_request(req)
        self.assertIsNone(res)

    def test_safe_relative_redirect_allowed(self):
        Redirect.objects.create(
            old_path='/old-projects',
            new_path='/projects/',
            status_code=301,
            is_active=True
        )
        req = self.factory.get('/old-projects')
        res = self.middleware.process_request(req)
        self.assertIsNotNone(res)
        self.assertEqual(res.status_code, 301)
        self.assertEqual(res['Location'], '/projects/')


class SecurityHeadersTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_security_headers_present(self):
        res = self.client.get('/')
        self.assertEqual(res['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(res['Referrer-Policy'], 'strict-origin-when-cross-origin')
        self.assertEqual(res['Cross-Origin-Opener-Policy'], 'same-origin-allow-popups')
        self.assertIn('Content-Security-Policy', res)
        self.assertIn("frame-ancestors 'self'", res['Content-Security-Policy'])


class WSGIProtectionTests(TestCase):
    def test_wsgi_crash_handler_suppresses_traceback(self):
        captured_status = []
        captured_headers = []

        def mock_start_response(status, headers):
            captured_status.append(status)
            captured_headers.append(headers)

        # Mock django_app raising an unhandled exception
        with patch.object(projectshub.wsgi, 'django_app', side_effect=RuntimeError("Database secret blown!")):
            body = projectshub.wsgi.application({}, mock_start_response)

        self.assertEqual(captured_status[0], "500 Internal Server Error")
        content = b"".join(body).decode('utf-8')
        # Ensure raw Python traceback or internal exception text is suppressed
        self.assertNotIn("Database secret blown!", content)
        self.assertNotIn("Traceback", content)
        self.assertIn("500 Internal Server Error", content)
