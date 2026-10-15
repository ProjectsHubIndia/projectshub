from django.test import TestCase

from core.live_chat import automated_answer
from core.models import BlogPost, FAQ, PricingPlan, Project, Service


class WebsiteKnowledgeAnswerTests(TestCase):
    def test_published_faq_answers_are_retrieved_and_drafts_are_ignored(self):
        FAQ.objects.create(
            question='How do I enroll in a workshop?',
            answer='Complete the workshop enrollment form.',
            is_published=True,
        )
        FAQ.objects.create(
            question='How do I enroll in a workshop?',
            answer='This internal draft must not be shown.',
            is_published=False,
        )

        answer = automated_answer('How do I enroll in a workshop?')

        self.assertIn('Complete the workshop enrollment form.', answer)
        self.assertNotIn('internal draft', answer)

    def test_published_service_details_are_matched(self):
        Service.objects.create(
            title='AI Automation',
            slug='ai-automation',
            short_description='Automate repetitive business workflows.',
            is_published=True,
        )

        answer = automated_answer('Tell me about AI automation')

        self.assertIn('Automate repetitive business workflows.', answer)
        self.assertIn('/services/ai-automation/', answer)

    def test_active_pricing_plans_are_used_instead_of_generic_pricing(self):
        PricingPlan.objects.create(name='Starter', monthly_price='25.00', yearly_price='240.00', is_active=True)
        PricingPlan.objects.create(name='Hidden', monthly_price='99.00', yearly_price='900.00', is_active=False)

        answer = automated_answer('What is the pricing?')

        self.assertIn('Starter: monthly 25.00, yearly 240.00', answer)
        self.assertNotIn('Hidden', answer)
        self.assertIn('does not specify a currency', answer)

    def test_published_blog_article_can_be_found_without_using_an_llm(self):
        BlogPost.objects.create(
            title='Building a RAG chatbot',
            slug='building-rag-chatbot',
            lead='A guide to retrieval-augmented generation.',
            is_active=True,
            is_published=True,
        )

        answer = automated_answer('Do you have a blog article about RAG chatbots?')

        self.assertIn('Building a RAG chatbot', answer)
        self.assertIn('retrieval-augmented generation', answer)
        self.assertIn('/blog/building-rag-chatbot/', answer)

    def test_existing_project_answers_remain_available(self):
        project = Project.objects.create(
            title='Customer Churn Pipeline',
            slug='customer-churn-pipeline',
            description='Predicts which customers are likely to leave.',
            detailed_description='A workflow for identifying churn risks.',
            category='ml',
            tags='Python, XGBoost',
            is_active=True,
            is_published=True,
        )

        answer = automated_answer('What does this project do?', project.get_absolute_url())

        self.assertIn(project.title, answer)
        self.assertIn('A workflow for identifying churn risks.', answer)
