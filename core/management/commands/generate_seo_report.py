import csv
import re
from django.core.management.base import BaseCommand
from django.test import Client


class Command(BaseCommand):
    help = 'Generate seo_report.csv comparing titles, meta descriptions, H1s, and canonical tags'

    def handle(self, *args, **options):
        client = Client()
        pages = [
            ('/', 'Homepage'),
            ('/projects/', 'Projects Showcase'),
            ('/tools/', 'Free Tools Directory'),
            ('/case-studies/', 'Case Studies'),
            ('/services/ai-development/', 'Service: AI Development'),
            ('/services/ai-automation/', 'Service: AI Automation'),
            ('/services/ai-integration/', 'Service: AI Integration'),
            ('/industries/', 'Industries'),
            ('/ai-roadmap/', 'AI Roadmap'),
            ('/workshop/', 'Workshops'),
            ('/blog/', 'Blog Articles'),
            ('/privacy/', 'Privacy Policy'),
            ('/terms/', 'Terms'),
        ]

        title_re = re.compile(r'<title>([^<]+)</title>', re.IGNORECASE)
        meta_desc_re = re.compile(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', re.IGNORECASE)
        canonical_re = re.compile(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']*)["\']', re.IGNORECASE)
        h1_re = re.compile(r'<h1[^>]*>(.*?)</h1>', re.IGNORECASE | re.DOTALL)

        rows = []
        for url, name in pages:
            res = client.get(url, follow=True)
            html = res.content.decode('utf-8', errors='ignore')

            t_match = title_re.search(html)
            m_match = meta_desc_re.search(html)
            c_match = canonical_re.search(html)
            h_match = h1_re.search(html)

            title = t_match.group(1).strip() if t_match else 'MISSING'
            meta_desc = m_match.group(1).strip() if m_match else 'MISSING'
            canonical = c_match.group(1).strip() if c_match else 'MISSING'
            h1_raw = h_match.group(1) if h_match else 'MISSING'
            h1_clean = re.sub(r'<[^>]+>', '', h1_raw).strip() if h1_raw != 'MISSING' else 'MISSING'

            status = 'PRESERVED'
            if title == 'MISSING' or meta_desc == 'MISSING' or h1_clean == 'MISSING':
                status = 'NEEDS_ATTENTION'

            rows.append({
                'URL': url,
                'Page Name': name,
                'Title': title,
                'Meta Description': meta_desc[:120] + '...' if len(meta_desc) > 120 else meta_desc,
                'Canonical Tag': canonical,
                'Primary H1': h1_clean[:80],
                'SEO Status': status,
            })

        csv_file = 'seo_report.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'URL', 'Page Name', 'Title', 'Meta Description', 'Canonical Tag', 'Primary H1', 'SEO Status'
            ])
            writer.writeheader()
            writer.writerows(rows)

        self.stdout.write(self.style.SUCCESS(f'[OK] Generated SEO audit report -> {csv_file}'))
