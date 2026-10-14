"""
Smoke tests for admin URLs reported as broken.
Verifies that all admin assets and ToolCategory URLs return 200 for staff users.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

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
