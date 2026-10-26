"""Create a source release; no builds, secrets, local media or experiment files."""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile

ROOTS = ('apps/api', 'apps/web', 'content', 'packages', 'deploy', 'docs', 'scripts', '.github',
         'README.md', 'package.json', 'package-lock.json', 'docker-compose.yml',
         'docker-compose.production.yml', '.dockerignore', '.env.example', '.gitignore')
EXCLUDED = {'node_modules', '.next', '.next-dev', '.git', '.gradle', 'build', 'dist',
            '__pycache__', '.pytest_cache', '.ruff_cache', '.mypy_cache', '.cache',
            'test-results', 'test-media', 'playwright-report', 'blob-report', 'coverage',
            '.verification', 'media', 'downloads', 'logs', 'tmp', 'temp', '.DS_Store'}
FORBIDDEN_SUFFIXES = {'.log', '.sqlite', '.sqlite3', '.db', '.dump', '.bak', '.sql', '.pyc',
                      '.pyo', '.pem', '.key', '.jks', '.keystore', '.p12', '.pfx', '.env',
                      '.apk', '.aab', '.tsbuildinfo', '.exit', '.har', '.zip', '.gz', '.tgz'}
MEDIA_SUFFIXES = {'.mp4', '.mov', '.webm', '.mkv', '.avi', '.mp3', '.wav', '.m4a', '.gif',
                  '.png', '.jpg', '.jpeg', '.webp'}
REQUIRED = ('apps/api/Dockerfile', 'apps/api/requirements.txt', 'apps/api/alembic.ini',
            'apps/api/app/main.py', 'apps/api/migrations/env.py', 'apps/web/Dockerfile',
            'apps/web/package.json', 'apps/web/next.config.ts', 'apps/web/tsconfig.json',
            'apps/web/postcss.config.mjs', 'apps/web/src/app/globals.css',
            'content/editorial/articles.json', 'content/pages/publication.json',
            'content/translations/pages.json', 'content/processing/tools.json',
            'package-lock.json', 'deploy/production.env.example', 'deploy/compose.ingress.yml',
            'deploy/nginx/socialviddownloader.conf.example', 'docs/manual-deployment.md',
            'docs/launch-checklist.md', 'docs/launch-freeze.json', 'docs/backups.md',
            'scripts/smoke-production.mjs', 'scripts/smoke-sitemap.mjs')


def excluded(path):
    if any(p in EXCLUDED or p.startswith('.venv') for p in path.parts):
        return True
    name = path.name.lower()
    if name.startswith('.env') and path.as_posix() != '.env.example':
        return True
    if name in {'local.properties', '.npmrc', '.pypirc', 'credentials', 'id_rsa', 'id_ed25519'}:
        return True
    if any(marker in name for marker in ('.sqlite-', '.sqlite3-', '.db-')):
        return True
    if path.suffix.lower() in FORBIDDEN_SUFFIXES:
        return True
    # Keep actual website assets, but exclude evidence screenshots and fixture media.
    return path.suffix.lower() in MEDIA_SUFFIXES and not path.as_posix().startswith(('apps/web/public/', 'apps/web/src/'))


def collect(root):
    result = []
    for entry in ROOTS:
        start = root / entry
        if not start.exists():
            raise ValueError(f'Missing source root: {entry}')
        if start.is_file():
            candidates = [start]
        else:
            candidates = []
            for directory, dirs, files in os.walk(start, followlinks=False):
                for name in dirs + files:
                    path = Path(directory) / name
                    if path.is_symlink():
                        raise ValueError(f'Review symlink before packaging: {path.relative_to(root)}')
                dirs[:] = [name for name in dirs if not excluded((Path(directory) / name).relative_to(root))]
                candidates.extend(Path(directory) / name for name in files)
        for path in candidates:
            if not excluded(path.relative_to(root)):
                if path.is_symlink() or not path.is_file():
                    raise ValueError(f'Not a regular source file: {path}')
                result.append(path)
    result.sort()
    names = {p.relative_to(root).as_posix() for p in result}
    missing = set(REQUIRED) - names
    if missing or not any(p.startswith('apps/api/migrations/versions/') and p.endswith('.py') for p in names):
        raise ValueError(f'Missing required application/migration files: {sorted(missing)}')
    return result


def validate_archive(path):
    with tarfile.open(path, 'r:gz') as archive:
        members = archive.getmembers()
        names = [m.name for m in members]
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive members')
        for member in members:
            parts = Path(member.name).parts
            if not member.isfile() or not parts or parts[0] != 'socialviddownloader' or '..' in parts:
                raise ValueError('Unsafe archive member')
        manifest = json.load(archive.extractfile('socialviddownloader/RELEASE-SHA256.json'))
        expected = {'socialviddownloader/' + name for name in manifest}
        if set(names) != expected | {'socialviddownloader/RELEASE-SHA256.json'}:
            raise ValueError('Manifest membership mismatch')
        if not set(REQUIRED).issubset(manifest):
            raise ValueError('Archive missing required files')
        for name, digest in manifest.items():
            if excluded(Path(name)) or name.startswith('apps/android-status-saver/'):
                raise ValueError(f'Excluded file in archive: {name}')
            data = archive.extractfile('socialviddownloader/' + name).read()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError(f'Hash mismatch: {name}')
    return len(manifest)


def package(root, target):
    if target.exists() or Path(str(target) + '.sha256').exists():
        raise ValueError('Output must not already exist')
    files = collect(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Stage and validate before exposing the final archive name.
    fd, name = tempfile.mkstemp(prefix='.svd-release-', suffix='.tar.gz', dir=target.parent)
    os.close(fd)
    staging = Path(name)
    try:
        manifest = {}
        with tarfile.open(staging, 'w:gz') as archive:
            for path in files:
                relative = path.relative_to(root).as_posix()
                body = path.read_bytes()
                manifest[relative] = hashlib.sha256(body).hexdigest()
                info = tarfile.TarInfo('socialviddownloader/' + relative)
                info.size = len(body)
                info.mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
                archive.addfile(info, io.BytesIO(body))
            body = (json.dumps(manifest, indent=2) + '\n').encode()
            info = tarfile.TarInfo('socialviddownloader/RELEASE-SHA256.json')
            info.size, info.mode = len(body), 0o644
            archive.addfile(info, io.BytesIO(body))
        count = validate_archive(staging)
        digest = hashlib.sha256(staging.read_bytes()).hexdigest()
        os.link(staging, target)  # Exclusive creation, never overwrites an existing release.
        with Path(str(target) + '.sha256').open('x') as checksum:
            checksum.write(f'{digest}  {target.name}\n')
        print(json.dumps({'archive': str(target), 'files': count, 'bytes': target.stat().st_size,
                          'sha256': digest, 'archiveValidation': 'PASS'}))
    finally:
        staging.unlink(missing_ok=True)


if __name__ == '__main__':
    if len(sys.argv) != 2 or not sys.argv[1].endswith('.tar.gz'):
        raise SystemExit('Usage: python3 scripts/package-release.py /path/to/new-release.tar.gz')
    package(Path(__file__).resolve().parents[1], Path(sys.argv[1]).resolve())
