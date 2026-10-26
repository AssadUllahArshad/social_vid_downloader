"""Fresh child resource limits, then exec FFmpeg without a shell."""

import json
import os
import resource
import sys

payload = json.load(sys.stdin)
resource.setrlimit(resource.RLIMIT_FSIZE, (payload["bytes"], payload["bytes"]))
resource.setrlimit(resource.RLIMIT_CPU, (payload["seconds"], payload["seconds"] + 1))
resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))
if sys.platform == "linux":
    resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 1024, 1024 * 1024 * 1024))
os.chdir(payload["cwd"])
os.execv(payload["command"][0], payload["command"])
