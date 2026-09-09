import json
from django.test import TestCase, Client
from django.urls import reverse
from core.models import ContactInquiry


class ContactLeadTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_contact_submission_success(self):
        from django.core import signing
        c_res = self.client.get(reverse('api_captcha'))
        token = c_res.json()['token']
        code = signing.loads(token, salt='captcha-salt')

        payload = {
            "full_name": "Test User",
            "email": "test@example.com",
            "subject": "Custom AI Project",
            "message": "Looking for a custom recommendation engine.",
            "catch_code": code,
            "captcha_token": token,
        }
        res = self.client.post(
            reverse('contact_submit'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('success'))

        inquiry = ContactInquiry.objects.filter(email="test@example.com").first()
        self.assertIsNotNone(inquiry)
        self.assertEqual(inquiry.name, "Test User")
        self.assertEqual(inquiry.subject, "Custom AI Project")

    def test_contact_submission_validation_error(self):
        payload = {
            "full_name": "",
            "email": "invalid-email",
            "message": ""
        }
        res = self.client.post(
            reverse('contact_submit'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertFalse(data.get('success'))
