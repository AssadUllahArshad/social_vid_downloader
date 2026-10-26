"""One bounded extraction per process, no user-controlled command arguments."""

import json
import resource
import sys

from .extractor import extract_metadata
from .media_errors import MediaError


def main():
    resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))
    resource.setrlimit(resource.RLIMIT_FSIZE, (32 * 1024 * 1024, 32 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CPU, (90, 90))
    request = json.loads(sys.stdin.read(8192))
    try:
        record = extract_metadata(request["url"], request["platform"])
        fields = {
            "url",
            "ext",
            "http_headers",
            "format_id",
            "height",
            "width",
            "vcodec",
            "acodec",
            "language",
            "protocol",
            "filesize",
            "filesize_approx",
            "audio_streams",
            "audio_stream_index",
            "audio_bitrate",
        }
        for selection in record["selections"].values():
            selection["video"] = {k: v for k, v in selection["video"].items() if k in fields}
            selection["tracks"] = [{k: v for k, v in track.items() if k in fields} for track in selection["tracks"]]
            for option in selection["audio_options"].values():
                option["source"] = {k: v for k, v in option["source"].items() if k in fields}
        print(json.dumps({"success": True, "record": record}))
    except MediaError as exc:
        print(json.dumps({"success": False, "error": {"code": exc.code, "message": exc.message, "status": exc.status}}))


if __name__ == "__main__":
    main()
