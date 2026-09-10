from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import AdminGuideNote

User = get_user_model()


class AdminGuideTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='secretpassword123'
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='secretpassword123'
        )
        self.note = AdminGuideNote.objects.create(
            title="Test SOP Checklist Note",
            category="branding",
            content="Instructions for updating brand assets.",
            action_url="/admin/core/sitesettings/1/change/",
            action_label="Edit Branding",
            is_pinned=True,
            is_completed=False,
            order=1
        )

    def test_admin_guide_anonymous_redirect(self):
        """Anonymous access to /admin/guide/ must redirect to login."""
        res = self.client.get('/admin/guide/')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/admin/login/', res.url)

    def test_admin_guide_non_staff_redirect(self):
        """Non-staff user must redirect to login with next parameter."""
        self.client.login(username='regularuser', password='secretpassword123')
        res = self.client.get('/admin/guide/')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/admin/login/', res.url)

    def test_admin_guide_superuser_access(self):
        """Staff superuser gets 200 OK with full manual and custom notes."""
        self.client.login(username='adminuser', password='secretpassword123')
        res = self.client.get('/admin/guide/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Project Guide &amp; Operations Manual")
        self.assertContains(res, "Test SOP Checklist Note")
        self.assertContains(res, "Edit Branding")

    def test_admin_guide_note_changelist_and_add(self):
        """Admin can view the AdminGuideNote changelist and add form."""
        self.client.login(username='adminuser', password='secretpassword123')
        res_list = self.client.get('/admin/core/adminguidenote/')
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, "Test SOP Checklist Note")

        res_add = self.client.get('/admin/core/adminguidenote/add/')
        self.assertEqual(res_add.status_code, 200)

    def test_toggle_guide_note_endpoint(self):
        """Toggling a guide note via AJAX flips is_completed status."""
        self.client.login(username='adminuser', password='secretpassword123')
        self.assertFalse(self.note.is_completed)

        res = self.client.post(f'/admin/guide/toggle/{self.note.id}/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'ok')
        self.assertTrue(data['is_completed'])

        self.note.refresh_from_db()
        self.assertTrue(self.note.is_completed)

        # Toggle back
        res2 = self.client.post(f'/admin/guide/toggle/{self.note.id}/')
        self.assertEqual(res2.status_code, 200)
        self.assertFalse(res2.json()['is_completed'])
        self.note.refresh_from_db()
        self.assertFalse(self.note.is_completed)
