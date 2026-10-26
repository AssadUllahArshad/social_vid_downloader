"""Remove expired server-controlled media folders; preserves active jobs and symlinks."""
import time
from app.config import settings
from app.main import root, sweep_stale_media
sweep_stale_media(root, time.time(), settings.file_ttl_seconds + settings.download_timeout_seconds)
print('Stale media cleanup complete.')
