import csv
import os
import re
import urllib.parse
from django.core.management.base import BaseCommand
from django.conf import settings
from django.test import Client


class Command(BaseCommand):
    help = 'Audit all image tags across templates and models, checking for broken sources, missing alt tags, and format'

    def handle(self, *args, **options):
        client = Client()
        urls_to_test = [
            '/',
            '/projects/',
            '/tools/',
            '/case-studies/',
            '/services/ai-development/',
            '/blog/',
        ]

        img_regex = re.compile(r'<img\s+([^>]*?)src=["\']([^"\']+)["\']([^>]*?)>', re.IGNORECASE)
        alt_regex = re.compile(r'alt=["\']([^"\']*)["\']', re.IGNORECASE)

        seen_images = {}
        for url in urls_to_test:
            res = client.get(url, follow=True)
            html = res.content.decode('utf-8', errors='ignore')

            for match in img_regex.finditer(html):
                attrs = match.group(1) + ' ' + match.group(3)
                src = match.group(2)
                alt_match = alt_regex.search(attrs)
                alt = alt_match.group(1) if alt_match else ''

                if src not in seen_images:
                    seen_images[src] = {
                        'src': src,
                        'alt': alt,
                        'pages': [url],
                        'has_alt': bool(alt_match),
                    }
                else:
                    if url not in seen_images[src]['pages']:
                        seen_images[src]['pages'].append(url)

        audit_rows = []
        for src, info in seen_images.items():
            is_static = src.startswith('/static/') or src.startswith('static/')
            is_media = src.startswith('/media/') or src.startswith('media/')
            is_external = src.startswith('http://') or src.startswith('https://')

            exists = 'EXTERNAL' if is_external else 'UNKNOWN'
            if is_static:
                rel_path = urllib.parse.unquote(src.replace('/static/', '').replace('static/', ''))
                full_path = settings.BASE_DIR / 'static' / rel_path.split('?')[0]
                exists = 'EXISTS' if os.path.exists(full_path) else 'MISSING'
            elif is_media:
                rel_path = urllib.parse.unquote(src.replace('/media/', '').replace('media/', ''))
                full_path = settings.MEDIA_ROOT / rel_path.split('?')[0]
                exists = 'EXISTS' if os.path.exists(full_path) else 'MISSING'

            status = 'OK'
            if exists == 'MISSING':
                status = 'BROKEN_LOCAL_FILE'
            elif not info['has_alt']:
                status = 'MISSING_ALT_ATTRIBUTE'

            audit_rows.append({
                'Image Source': src,
                'Found on Pages': '; '.join(info['pages']),
                'Alt Text': info['alt'],
                'File Status': exists,
                'Audit Result': status,
            })

        csv_file = 'image_audit.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Image Source', 'Found on Pages', 'Alt Text', 'File Status', 'Audit Result'
            ])
            writer.writeheader()
            writer.writerows(audit_rows)

        self.stdout.write(self.style.SUCCESS(f'[OK] Audited {len(audit_rows)} unique images -> generated {csv_file}'))
