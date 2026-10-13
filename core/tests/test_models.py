from django.test import TestCase
from core.models import (
    Project, ProjectCategory, Technology, AITool, ToolCategory,
    Service, CaseStudy, Testimonial, FAQ, ContactInquiry, SiteSettings, Redirect
)


class ModelTests(TestCase):
    def setUp(self):
        self.category = ProjectCategory.objects.create(
            name="Machine Learning",
            slug="machine-learning",
            icon="ml"
        )
        self.tech = Technology.objects.create(
            name="Python",
            slug="python"
        )
        self.project = Project.objects.create(
            title="AI Text Classifier",
            slug="ai-text-classifier",
            category="ml",
            category_ref=self.category,
            description="A test ML classification project.",
            price=0,
            is_active=True
        )
        self.project.technologies.add(self.tech)

    def test_project_creation_and_str(self):
        self.assertEqual(str(self.project), "AI Text Classifier")
        self.assertEqual(self.project.slug, "ai-text-classifier")
        self.assertTrue(self.project.is_active)
        self.assertIn(self.tech, self.project.technologies.all())

    def test_contact_inquiry_creation(self):
        inquiry = ContactInquiry.objects.create(
            name="John Doe",
            email="john@example.com",
            subject="Test Inquiry",
            message="Hello, I need custom AI development.",
            status="new"
        )
        self.assertEqual(str(inquiry), "John Doe (john@example.com) — Test Inquiry")
        self.assertEqual(inquiry.status, "new")

    def test_contact_inquiry_has_required_admin_fields(self):
        """Ensure ContactInquiry has all fields referenced in admin.py."""
        inquiry = ContactInquiry.objects.create(
            name="Test User",
            email="test@example.com",
            phone="+91 9876543210",
            subject="Service Inquiry", 
            message="I need AI services",
            status="new",
            source_page="/contact/",
            admin_notes="Test admin notes"
        )
        
        # Check that all admin.py fields exist and are accessible
        self.assertTrue(hasattr(inquiry, 'name'))
        self.assertTrue(hasattr(inquiry, 'email'))
        self.assertTrue(hasattr(inquiry, 'phone'))
        self.assertTrue(hasattr(inquiry, 'subject'))
        self.assertTrue(hasattr(inquiry, 'message'))
        self.assertTrue(hasattr(inquiry, 'status'))
        self.assertTrue(hasattr(inquiry, 'admin_notes'))
        self.assertTrue(hasattr(inquiry, 'ip_address'))
        self.assertTrue(hasattr(inquiry, 'created_at'))
        
        # Verify field values
        self.assertEqual(inquiry.name, "Test User")
        self.assertEqual(inquiry.email, "test@example.com")
        self.assertEqual(inquiry.phone, "+91 9876543210")
        self.assertEqual(inquiry.subject, "Service Inquiry")
        self.assertEqual(inquiry.admin_notes, "Test admin notes")

    def test_site_settings_singleton(self):
        settings = SiteSettings.get_settings()
        self.assertIsNotNone(settings)
        self.assertEqual(str(settings), "ProjectsHub Settings")

    def test_redirect_creation(self):
        redirect = Redirect.objects.create(
            old_path="/old-work/",
            new_path="/projects/",
            status_code=301,
            is_active=True
        )
        self.assertEqual(str(redirect), "/old-work/ -> /projects/ (301)")

    def test_case_study_creation_and_properties(self):
        cs = CaseStudy.objects.create(
            title="AI Document Summarizer for Law Firms",
            client="LexAI — Startup",
            industry="LegalTech",
            summary="A law firm startup needed an AI-powered document summarizer.",
            featured_image="case_studies/lexai_doc_summarizer.jpg",
            is_published=True
        )
        self.assertEqual(str(cs), "AI Document Summarizer for Law Firms (LexAI — Startup)")
        self.assertEqual(cs.client_name, "LexAI — Startup")
        self.assertEqual(cs.slug, "ai-document-summarizer-for-law-firms")
        self.assertTrue(bool(cs.featured_image))

