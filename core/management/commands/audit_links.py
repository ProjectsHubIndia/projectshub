import csv
import re
from urllib.parse import urlparse
from django.core.management.base import BaseCommand
from django.test import Client


class Command(BaseCommand):
    help = 'Audit all internal and external links across the site and generate link_audit.csv'

    def handle(self, *args, **options):
        client = Client()
        start_pages = [
            '/',
            '/projects/',
            '/tools/',
            '/case-studies/',
            '/services/ai-development/',
            '/blog/',
        ]

        link_regex = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
        found_links = {}

        for page in start_pages:
            res = client.get(page, follow=True)
            html = res.content.decode('utf-8', errors='ignore')

            for match in link_regex.finditer(html):
                href = match.group(1).strip()
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue

                if href not in found_links:
                    found_links[href] = [page]
                elif page not in found_links[href]:
                    found_links[href].append(page)

        audit_rows = []
        for href, pages in found_links.items():
            parsed = urlparse(href)
            is_external = bool(parsed.scheme in ('http', 'https') and 'projectshub.co.in' not in parsed.netloc and '127.0.0.1' not in parsed.netloc)
            is_special = href.startswith('tel:') or href.startswith('mailto:')

            status_code = '-'
            status = 'OK'

            if not is_external and not is_special:
                clean_path = parsed.path or '/'
                try:
                    res = client.get(clean_path, follow=True)
                    status_code = res.status_code
                    if res.status_code == 404:
                        status = 'BROKEN_404'
                    elif res.status_code >= 500:
                        status = f'SERVER_ERROR_{res.status_code}'
                    else:
                        status = 'OK_INTERNAL'
                except Exception as e:
                    status = f'ERROR_{str(e)}'
            elif is_special:
                status = 'SPECIAL_PROTOCOL_OK'
            else:
                status = 'EXTERNAL_LINK'

            audit_rows.append({
                'Link URL': href,
                'Found On': '; '.join(pages),
                'Link Type': 'External' if is_external else ('Special' if is_special else 'Internal'),
                'HTTP Response': status_code,
                'Status': status,
            })

        csv_file = 'link_audit.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Link URL', 'Found On', 'Link Type', 'HTTP Response', 'Status'
            ])
            writer.writeheader()
            writer.writerows(audit_rows)

        self.stdout.write(self.style.SUCCESS(f'[OK] Audited {len(audit_rows)} links -> generated {csv_file}'))
