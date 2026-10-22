import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CI_SECRET_KEY = 'ci-only-not-a-production-secret-key-1234567890-abcdefghijklmnopqrstuvwxyz'


class VercelDatabaseConfigurationTests(SimpleTestCase):
    def import_settings(self, database_url=None):
        env = os.environ.copy()
        for name in ('DATABASE_URL', 'POSTGRES_URL', 'POSTGRES_URL_NON_POOLING'):
            env.pop(name, None)
        env.update({
            'DEBUG': 'False',
            'ENVIRONMENT': 'production',
            'SECRET_KEY': CI_SECRET_KEY,
            'VERCEL': '1',
        })
        if database_url:
            env['DATABASE_URL'] = database_url
        return subprocess.run(
            [sys.executable, '-c', 'import projectshub.settings'],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
        )

    def test_production_vercel_requires_postgresql(self):
        result = self.import_settings()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('PostgreSQL DATABASE_URL', result.stderr)

    def test_production_vercel_accepts_postgresql_url(self):
        result = self.import_settings('postgres://user:password@localhost:5432/projectshub')

        self.assertEqual(result.returncode, 0, result.stderr)
