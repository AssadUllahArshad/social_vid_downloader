"""Write an owner-only token file for existing read-only provider diagnostics."""
import argparse
import os
import secrets
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', required=True, help='New private file; existing files are never replaced')
args = parser.parse_args()
path = Path(args.output)
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as handle:
    handle.write('ADMIN_PROVIDER_TOKEN=' + secrets.token_urlsafe(48) + '\n')
print('Private token file created. Transfer its value into your secret manager; do not commit it.')
