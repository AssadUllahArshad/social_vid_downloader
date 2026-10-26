"""Focused release packaging checks; no application server or build required."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('release', Path(__file__).with_name('package-release.py'))
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class PackageChecks(unittest.TestCase):
    def test_excludes_private_generated_and_media_files(self):
        for name in ['.env', '.env.production', 'apps/api/.env.example', 'deploy/live.env',
                     'apps/api/local.sqlite-wal', 'apps/api/local.db-shm', 'data.sqlite3',
                     'apps/web/test-media/source.mov', 'docs/live/output.mp4', 'docs/evidence.png',
                     'apps/web/tsconfig.tsbuildinfo', 'apps/web/.next/BUILD_ID',
                     'apps/web/test-results/result.json', 'apps/api/.venv/lib/file.py',
                     'deploy/server.key', '.npmrc', 'docs/verification.log.exit']:
            with self.subTest(name=name):
                self.assertTrue(release.excluded(Path(name)))

    def test_keeps_dependencies_content_migrations_and_public_assets(self):
        for name in [*release.REQUIRED, '.env.example', 'apps/web/public/example.png',
                     'apps/web/src/app/preview.png', 'apps/api/migrations/versions/0001_initial.py']:
            with self.subTest(name=name):
                self.assertFalse(release.excluded(Path(name)))

    def test_actual_source_selection_is_complete_and_excludes_android(self):
        root = Path(__file__).resolve().parents[1]
        files = release.collect(root)
        self.assertTrue(set(release.REQUIRED).issubset({p.relative_to(root).as_posix() for p in files}))
        self.assertFalse(any('android-status-saver' in p.parts for p in files))

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'existing.tar.gz'
            target.write_bytes(b'preserve')
            with self.assertRaises(ValueError):
                release.package(Path(folder), target)
            self.assertEqual(target.read_bytes(), b'preserve')


if __name__ == '__main__':
    unittest.main()
