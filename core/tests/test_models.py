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

