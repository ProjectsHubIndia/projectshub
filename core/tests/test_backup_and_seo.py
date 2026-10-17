"""Backup restore robustness, admin database updates, and the SEO dashboard."""
import json
import hashlib
import io
import os
import shutil
import tempfile
import zipfile
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from core import backup_tools, seo_audit
from core.models import BlogPost, Redirect, SEOData


class BackupRestoreTests(TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.override = override_settings(
            BASE_DIR=self.tmp,
            MEDIA_ROOT=os.path.join(self.tmp, 'media'),
        )
        self.override.enable()
        self.su = get_user_model().objects.create_superuser('su', 'su@example.com', 'pw-Strong-123!')
        self.client.force_login(self.su)

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def upload(self, objects, name='backup.json'):
        f = SimpleUploadedFile(name, json.dumps(objects).encode(), content_type='application/json')
        return self.client.post('/admin/backup/restore/', {'backup_file': f}, follow=True)

    def test_backup_from_another_site_with_different_ids_restores(self):
        # Local copy has /admin under id 7; the live backup has it under id 8 (the reported error).
        Redirect.objects.create(pk=7, old_path='/admin', new_path='/admin/')
        backup = [
            {'model': 'core.redirect', 'pk': 8, 'fields': {'old_path': '/admin', 'new_path': '/admin/', 'status_code': 301, 'is_active': True, 'notes': 'from live'}},
            {'model': 'core.redirect', 'pk': 1, 'fields': {'old_path': '/portfolio/', 'new_path': '/projects/', 'status_code': 301, 'is_active': True, 'notes': ''}},
        ]
        res = self.upload(backup)
        msgs = [str(m) for m in res.context['messages']]
        self.assertTrue(any('Restored 2 records' in m for m in msgs), msgs)
        self.assertEqual(Redirect.objects.filter(old_path='/admin').count(), 1)
        self.assertEqual(Redirect.objects.get(old_path='/admin').notes, 'from live')
        self.assertTrue(os.listdir(os.path.join(self.tmp, 'backups')), 'safety snapshot must be written')

    def upload_zip(self, members, name='full_backup.zip'):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            for arc, data in members.items():
                zf.writestr(arc, data)
        f = SimpleUploadedFile(name, buf.getvalue(), content_type='application/zip')
        return self.client.post('/admin/backup/restore/', {'backup_file': f}, follow=True)

    def test_zip_backup_restores_data_and_media(self):
        backup = [{'model': 'core.redirect', 'pk': 1, 'fields': {'old_path': '/old/', 'new_path': '/new/', 'status_code': 301, 'is_active': True, 'notes': ''}}]
        res = self.upload_zip({'database.json': json.dumps(backup), 'media/pages/logo.png': b'PNGDATA'})
        msgs = [str(m) for m in res.context['messages']]
        self.assertTrue(any('Restored 1 records' in m and '1 media file' in m for m in msgs), msgs)
        self.assertTrue(Redirect.objects.filter(old_path='/old/').exists())
        restored = os.path.join(self.tmp, 'media', 'pages', 'logo.png')
        self.assertTrue(os.path.isfile(restored))
        self.assertEqual(open(restored, 'rb').read(), b'PNGDATA')

    def test_zip_restore_blocks_path_traversal(self):
        backup = [{'model': 'core.redirect', 'pk': 1, 'fields': {'old_path': '/x/', 'new_path': '/y/', 'status_code': 301, 'is_active': True, 'notes': ''}}]
        self.upload_zip({'database.json': json.dumps(backup), 'media/../../evil.txt': b'pwned'})
        self.assertFalse(os.path.exists(os.path.join(self.tmp, 'evil.txt')))
        self.assertFalse(os.path.exists(os.path.join(os.path.dirname(self.tmp), 'evil.txt')))

    def test_foreign_keys_follow_remapped_ids(self):
        BlogPost.objects.create(pk=5, title='Local', slug='same-slug', is_active=True, is_published=True)
        backup = [
            {'model': 'core.blogpost', 'pk': 9, 'fields': {'title': 'From live', 'slug': 'same-slug', 'is_active': True, 'is_published': True}},
            {'model': 'core.blogsection', 'pk': 100, 'fields': {'post': 9, 'heading': 'Intro', 'order': 1}},
        ]
        self.upload(backup)
        post = BlogPost.objects.get(slug='same-slug')
        self.assertEqual(post.pk, 5)
        self.assertEqual(post.title, 'From live')
        self.assertEqual(post.sections.count(), 1)

    def test_fetch_imports_initial_data_json_from_the_deploy(self):
        fixture = [{'model': 'core.seodata', 'pk': 4, 'fields': {'path': '/fetched/', 'meta_title': 'T', 'meta_description': 'D'}}]
        with open(os.path.join(self.tmp, 'initial_data.json'), 'w', encoding='utf-8') as fh:
            json.dump(fixture, fh)
        res = self.client.post('/admin/backup/fetch/', {'source': 'fixture'}, follow=True)
        msgs = [str(m) for m in res.context['messages']]
        self.assertTrue(any('initial_data.json' in m and 'Restored 1 records' in m for m in msgs), msgs)
        self.assertTrue(SEOData.objects.filter(path='/fetched/').exists())

    def test_fetch_from_a_missing_fixture_reports_instead_of_failing(self):
        res = self.client.post('/admin/backup/fetch/', {'source': 'fixture'}, follow=True)
        self.assertTrue(any('no initial_data.json' in str(m) for m in res.context['messages']))

    def test_fetch_rejects_a_non_http_link(self):
        res = self.client.post('/admin/backup/fetch/', {'source': 'url', 'backup_url': 'file:///etc/passwd'}, follow=True)
        self.assertTrue(any('http:// or https://' in str(m) for m in res.context['messages']))

    def test_restoring_twice_is_safe(self):
        backup = [{'model': 'core.seodata', 'pk': 3, 'fields': {'path': '/x/', 'meta_title': 'T', 'meta_description': 'D'}}]
        self.upload(backup)
        self.upload(backup)
        self.assertEqual(SEOData.objects.filter(path='/x/').count(), 1)

    def test_download_bundle_includes_database_export_and_uploaded_media(self):
        image_path = os.path.join(self.tmp, 'media', 'blog', 'cover.png')
        os.makedirs(os.path.dirname(image_path))
        with open(image_path, 'wb') as image:
            image.write(b'test image bytes')

        response = self.client.get('/admin/backup/download-bundle/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        with zipfile.ZipFile(io.BytesIO(b''.join(response.streaming_content))) as bundle:
            self.assertIn('database.json', bundle.namelist())
            self.assertIn('database.sqlite3', bundle.namelist())
            self.assertIn('media/blog/cover.png', bundle.namelist())
            self.assertIn('README.txt', bundle.namelist())
            self.assertIn('manifest.json', bundle.namelist())
            self.assertEqual(bundle.read('media/blog/cover.png'), b'test image bytes')
            self.assertIsInstance(json.loads(bundle.read('database.json')), list)
            self.assertTrue(bundle.read('database.sqlite3').startswith(b'SQLite format 3\x00'))
            manifest = json.loads(bundle.read('manifest.json'))
            self.assertEqual(
                manifest['files']['media/blog/cover.png']['sha256'],
                hashlib.sha256(b'test image bytes').hexdigest(),
            )

    def test_zip_restore_rejects_bad_manifest_before_writing_files_or_data(self):
        fixture = json.dumps([
            {'model': 'core.redirect', 'pk': 1, 'fields': {
                'old_path': '/checksum/', 'new_path': '/target/', 'status_code': 301,
                'is_active': True, 'notes': '',
            }},
        ]).encode()
        manifest = {
            'format': 'projectshub-full-backup',
            'version': 1,
            'files': {
                'database.json': {'size': len(fixture), 'sha256': 'incorrect'},
                'media/pages/logo.png': {
                    'size': len(b'bad image'),
                    'sha256': hashlib.sha256(b'bad image').hexdigest(),
                },
            },
        }
        res = self.upload_zip({
            'database.json': fixture,
            'media/pages/logo.png': b'bad image',
            'manifest.json': json.dumps(manifest),
        })
        messages = ' '.join(str(message) for message in res.context['messages'])
        self.assertIn('SHA-256 check', messages)
        self.assertFalse(Redirect.objects.filter(old_path='/checksum/').exists())
        self.assertFalse(os.path.exists(os.path.join(self.tmp, 'media', 'pages', 'logo.png')))

    def test_zip_restore_rolls_back_media_if_database_restore_fails(self):
        destination = os.path.join(self.tmp, 'media', 'pages', 'logo.png')
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, 'wb') as existing:
            existing.write(b'previous image')
        backup = [{'model': 'core.redirect', 'pk': 1, 'fields': {
            'old_path': '/restore-failure/', 'new_path': '/target/', 'status_code': 301,
            'is_active': True, 'notes': '',
        }}]
        with mock.patch('core.backup_tools.restore_backup', side_effect=backup_tools.RestoreError('failed')):
            self.upload_zip({
                'database.json': json.dumps(backup),
                'media/pages/logo.png': b'replacement image',
            })
        with open(destination, 'rb') as restored:
            self.assertEqual(restored.read(), b'previous image')
        self.assertFalse(Redirect.objects.filter(old_path='/restore-failure/').exists())

    def test_invalid_files_are_rejected_without_changes(self):
        res = self.client.post('/admin/backup/restore/', {'backup_file': SimpleUploadedFile('b.json', b'not json')}, follow=True)
        self.assertTrue(any('not valid JSON' in str(m) for m in res.context['messages']))
        res = self.upload({'hello': 'world'})
        self.assertTrue(any('does not look like' in str(m) for m in res.context['messages']))

    def test_unknown_models_are_skipped_not_fatal(self):
        res = self.upload([
            {'model': 'oldapp.thing', 'pk': 1, 'fields': {}},
            {'model': 'core.seodata', 'pk': 1, 'fields': {'path': '/y/', 'meta_title': 'T', 'meta_description': 'D'}},
        ])
        msgs = ' '.join(str(m) for m in res.context['messages'])
        self.assertIn('Skipped', msgs)
        self.assertTrue(SEOData.objects.filter(path='/y/').exists())

    def test_restore_requires_superuser(self):
        staff = get_user_model().objects.create_user('st', 'st@example.com', 'pw-Strong-123!', is_staff=True)
        self.client.force_login(staff)
        res = self.client.post('/admin/backup/restore/', {})
        self.assertEqual(res.status_code, 302)
        self.assertIn('/admin/login/', res['Location'])


class MigrationBannerTests(TestCase):
    def setUp(self):
        self.su = get_user_model().objects.create_superuser('su', 'su@example.com', 'pw-Strong-123!')
        self.client.force_login(self.su)

    def test_banner_and_apply_button(self):
        with mock.patch('core.backup_tools.pending_migrations', return_value=['core.9999_future']):
            res = self.client.get('/admin/backup/')
            self.assertContains(res, 'Database update needed')
            self.assertContains(res, 'Apply database update')
        res = self.client.get('/admin/backup/')
        self.assertNotContains(res, 'Database update needed')

    def test_apply_view(self):
        with mock.patch('core.backup_tools.pending_migrations', return_value=['core.9999_future']), \
             mock.patch('core.backup_tools.apply_migrations', return_value='ok') as apply, \
             mock.patch('core.backup_tools.snapshot_db_file', return_value=None):
            res = self.client.post('/admin/maintenance/migrate/', {'next': '/admin/backup/'}, follow=True)
            apply.assert_called_once()
        self.assertTrue(any('Database updated' in str(m) for m in res.context['messages']))
        self.assertEqual(self.client.get('/admin/maintenance/migrate/').status_code, 405)

    def test_apply_rejects_offsite_next(self):
        res = self.client.post('/admin/maintenance/migrate/', {'next': 'https://evil.example/'})
        self.assertEqual(res['Location'], '/admin/')


@override_settings(CANONICAL_SITE_URL='https://projectshub.co.in', ALLOWED_HOSTS=['*'])
class SeoDashboardTests(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.staff = get_user_model().objects.create_user('ed', 'ed@example.com', 'pw-Strong-123!', is_staff=True)
        self.client.force_login(self.staff)

    def test_dashboard_audits_sitemap_pages(self):
        BlogPost.objects.create(title='Hi', slug='hi', is_active=True, is_published=True)
        res = self.client.get('/admin/seo/')
        self.assertEqual(res.status_code, 200)
        audit = res.context['audit']
        paths = [p['path'] for p in audit['pages']]
        self.assertIn('/', paths)
        self.assertIn('/blog/hi/', paths)
        self.assertContains(res, 'not a Google ranking metric')
        self.assertContains(res, 'Google Search Console')
        self.assertContains(res, 'sd-integrations-card')
        self.assertContains(res, 'Google Analytics')
        for p in audit['pages']:
            self.assertGreaterEqual(p['score'], 0)
            self.assertLessEqual(p['score'], 100)

    def test_noindex_page_in_sitemap_is_flagged_critical(self):
        client, _ = seo_audit._client()
        SEOData.objects.create(path='/terms/', meta_title='Terms', meta_description='x' * 80, robots='noindex, nofollow', is_indexable=True)
        page = seo_audit.audit_page(client, '/terms/')
        self.assertTrue(any(i['severity'] == 'critical' and i['check'] == 'Indexability' for i in page['issues']))

    def test_redirect_problems_listed(self):
        Redirect.objects.create(old_path='/industries/', new_path='/services/ai-development/')
        Redirect.objects.create(old_path='/a/', new_path='/b/')
        Redirect.objects.create(old_path='/b/', new_path='/c/')   # chain a -> b -> c
        result = seo_audit.run_audit()
        rules = ' '.join(r['rule'] + r['problem'] for r in result['redirect_problems'])
        self.assertIn('/a/ → /b/', rules)

    def test_run_and_export(self):
        res = self.client.post('/admin/seo/run/', follow=True)
        self.assertTrue(any('Audit finished' in str(m) for m in res.context['messages']))
        res = self.client.get('/admin/seo/export.csv')
        self.assertEqual(res['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('URL,Score,Severity', res.content.decode())

    def test_requires_staff(self):
        self.client.logout()
        self.assertEqual(self.client.get('/admin/seo/').status_code, 302)
