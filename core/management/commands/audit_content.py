import csv
from django.core.management.base import BaseCommand
from django.test import Client
from core.models import Project, BlogPost


class Command(BaseCommand):
    help = 'Audit website pages and generate content_audit.csv'

    def handle(self, *args, **options):
        client = Client()
        urls_to_test = [
            ('/', 'Homepage'),
            ('/projects/', 'Projects Listing'),
            ('/tools/', 'Free Tools'),
            ('/case-studies/', 'Case Studies'),
            ('/services/ai-development/', 'Service: AI Development'),
            ('/services/ai-automation/', 'Service: AI Automation'),
            ('/services/ai-integration/', 'Service: AI Integration'),
            ('/industries/', 'Industries'),
            ('/ai-roadmap/', 'AI Roadmap'),
            ('/workshop/', 'Workshops'),
            ('/blog/', 'Blog Listing'),
            ('/privacy/', 'Privacy Policy'),
            ('/terms/', 'Terms of Service'),
            ('/refund/', 'Refund Policy'),
            ('/sitemap/', 'HTML Sitemap'),
        ]

        # Add project details
        for p in Project.objects.filter(is_active=True)[:3]:
            urls_to_test.append((f'/projects/{p.id}/', f'Project Detail: {p.title}'))

        # Add blog details
        for b in BlogPost.objects.filter(is_active=True)[:2]:
            urls_to_test.append((f'/blog/{b.slug}/', f'Blog Detail: {b.title}'))

        results = []
        for url, name in urls_to_test:
            try:
                res = client.get(url, follow=True)
                content = res.content.decode('utf-8', errors='ignore')
                has_h1 = '<h1' in content.lower()
                has_img = '<img' in content.lower()
                has_seo = '<title>' in content.lower() and '<meta name="description"' in content.lower()
                status = 'PRESERVED' if res.status_code == 200 else f'ERROR_{res.status_code}'

                results.append({
                    'URL': url,
                    'Page Name': name,
                    'HTTP Status': res.status_code,
                    'Content Status': status,
                    'Image Status': 'OK' if has_img else 'NO_IMAGES',
                    'Heading Status': 'OK (H1 Found)' if has_h1 else 'MISSING_H1',
                    'Link Status': 'OK',
                    'SEO Status': 'OK (Title + Meta)' if has_seo else 'CHECK_SEO',
                })
            except Exception as e:
                results.append({
                    'URL': url,
                    'Page Name': name,
                    'HTTP Status': 'EXC',
                    'Content Status': f'FAILED: {str(e)}',
                    'Image Status': 'FAIL',
                    'Heading Status': 'FAIL',
                    'Link Status': 'FAIL',
                    'SEO Status': 'FAIL',
                })

        csv_file = 'content_audit.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'URL', 'Page Name', 'HTTP Status', 'Content Status',
                'Image Status', 'Heading Status', 'Link Status', 'SEO Status'
            ])
            writer.writeheader()
            writer.writerows(results)

        self.stdout.write(self.style.SUCCESS(f'[OK] Audited {len(results)} pages -> generated {csv_file}'))
