import json
from django.core.management.base import BaseCommand
from core.models import Project, AITool, Service, CaseStudy, Testimonial, FAQ, BlogPost


class Command(BaseCommand):
    help = 'Export and audit all existing ProjectsHub site data to JSON'

    def handle(self, *args, **options):
        self.stdout.write('Crawling local ProjectsHub site data...')
        
        data = {
            'site': 'ProjectsHub',
            'base_url': 'https://projectshub.co.in/',
            'projects': [
                {
                    'id': p.id,
                    'title': p.title,
                    'slug': p.slug,
                    'category': p.category,
                    'tags': p.tags,
                    'price': str(p.price),
                    'price_label': p.price_label,
                    'show_on_index': p.show_on_index,
                    'is_active': p.is_active,
                }
                for p in Project.objects.all()
            ],
            'tools': [
                {
                    'id': t.id,
                    'name': t.name,
                    'slug': t.slug,
                    'category': t.category_slug,
                    'url': t.external_url,
                }
                for t in AITool.objects.all()
            ],
            'services': [
                {
                    'id': s.id,
                    'title': s.title,
                    'slug': s.slug,
                    'target_audience': s.target_audience,
                    'features': [f.title for f in s.features.all()],
                }
                for s in Service.objects.all()
            ],
            'case_studies': [
                {
                    'id': cs.id,
                    'title': cs.title,
                    'slug': cs.slug,
                    'client': cs.client,
                    'industry': cs.industry,
                    'metrics': [{'label': m.label, 'value': m.value} for m in cs.metrics.all()],
                }
                for cs in CaseStudy.objects.all()
            ],
            'testimonials': [
                {
                    'id': tm.id,
                    'name': tm.name,
                    'role': tm.role,
                    'company': tm.company,
                    'rating': tm.rating,
                    'content': tm.content,
                }
                for tm in Testimonial.objects.all()
            ],
            'faqs': [
                {
                    'id': fq.id,
                    'question': fq.question,
                    'answer': fq.answer,
                }
                for fq in FAQ.objects.all()
            ],
            'blog_posts': [
                {
                    'id': bp.id,
                    'title': bp.title,
                    'slug': bp.slug,
                    'author': bp.author_name,
                    'published_at': str(bp.published_at),
                }
                for bp in BlogPost.objects.all()
            ]
        }

        out_path = 'site_crawl_data.json'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stdout.write(self.style.SUCCESS(f'[OK] Crawled and exported site data to {out_path}'))
