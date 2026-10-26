"""Real FFmpeg resource failures and source-preserving mute regressions."""
import logging
import subprocess
import threading

import pytest

from app.config import settings
from app.media_errors import MediaError
from app.processing.engine import Options, execute, process_files


def test_cpu_limit_is_specific(tmp_path, caplog):
    caplog.set_level(logging.INFO, logger="socialvid.processing")
    with pytest.raises(MediaError) as failure:
        execute(["-f", "lavfi", "-i", "testsrc2=size=1920x1080:rate=60", "-t", "600", "-c:v", "libx264",
                 "-preset", "veryslow", str(tmp_path / "out.mp4")], tmp_path, threading.Event(), 1)
    assert failure.value.code == "processing_timeout"
    assert str(tmp_path) not in caplog.text


def test_real_output_size_limit_is_specific(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "max_file_bytes", 4096)
    with pytest.raises(MediaError) as failure:
        execute(["-f", "lavfi", "-i", "testsrc2=size=320x180:rate=25", "-t", "5", "-c:v", "rawvideo",
                 str(tmp_path / "out.avi")], tmp_path, threading.Event(), 10)
    assert failure.value.code == "output_too_large"


def test_missing_encoder_is_specific(tmp_path):
    with pytest.raises(MediaError) as failure:
        execute(["-f", "lavfi", "-i", "color=size=64x64", "-t", "1", "-c:v", "svd_nonexistent_encoder",
                 str(tmp_path / "out.mp4")], tmp_path, threading.Event(), 10)
    assert failure.value.code == "unsupported_codec"


def test_encoder_threads_and_mute_packet_integrity(tmp_path):
    source = tmp_path / "source.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=25", "-f", "lavfi",
                    "-i", "sine", "-t", "1", "-c:v", "libx264", "-c:a", "aac", str(source)], check=True)
    result = process_files("remove-audio", [source], Options(), tmp_path / "mute", threading.Event())
    def packets(path):
        return subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0", "-c", "copy",
                                        "-f", "hash", "-hash", "sha256", "-"])
    assert packets(source) == packets(result["path"])
    directory = tmp_path / "encode"
    directory.mkdir()
    log = directory / "private.log"
    execute(["-i", str(source), "-an", "-c:v", "libx264", str(directory / "out.mp4")], directory,
            threading.Event(), 15, log)
    assert "threads=1 " in log.read_text()


def test_near_limit_upload_and_corruption(memory_store, tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from app import main
    source = tmp_path / "valid.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=160x90", "-t", "1",
                    "-c:v", "libx264", str(source)], check=True)
    data = source.read_bytes()
    monkeypatch.setattr(main.settings, "processing_enabled", True)
    monkeypatch.setattr(settings, "max_file_bytes", len(data))
    headers = {"Content-Type": "application/octet-stream"}
    with TestClient(main.app) as client:
        assert client.post("/processing/uploads", content=data, headers=headers).status_code == 200
        response = client.post("/processing/uploads", content=data + b"x", headers=headers)
        assert response.status_code == 413 and response.json()["error"]["code"] == "file_too_large"
        assert client.post("/processing/uploads", content=data[:100], headers=headers).status_code == 422


def test_real_ready_file_expiry_and_cleanup(memory_store, tmp_path, monkeypatch):
    import time

    from fastapi.testclient import TestClient

    from app import main
    from app.processing.api import sweep

    source = tmp_path / "expiring.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=size=64x64", "-t", "1",
                    "-c:v", "libx264", str(source)], check=True)
    monkeypatch.setattr(settings, "processing_enabled", True)
    monkeypatch.setattr(settings, "file_ttl_seconds", 2)
    with TestClient(main.app) as client:
        uploaded = client.post("/processing/uploads", content=source.read_bytes(), headers={"Content-Type": "application/octet-stream"}).json()
        created = client.post("/processing/jobs", json={"operation": "remove-audio", "upload_ids": [uploaded["uploadId"]]}).json()
        for _ in range(100):
            result = client.get(created["statusUrl"]).json()
            if result["status"] != "processing":
                break
            time.sleep(0.03)
        assert result["status"] == "ready"
        assert client.get(result["downloadUrl"]).status_code == 200
        time.sleep(2.1)
        assert client.get(result["downloadUrl"]).status_code == 410
        folder = main.root / "_processing" / created["jobId"]
        assert folder.exists()
        import os
        os.utime(folder, (0, 0))
        sweep(folder.parent)
        assert not folder.exists()


def test_splitter_retains_subframe_tail(tmp_path):
    import zipfile

    from app.processing.engine import inspect
    source = tmp_path / "fractional.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=24000/1001",
                    "-frames:v", "24", "-c:v", "libx264", str(source)], check=True)
    result = process_files("splitter", [source], Options(segment_seconds=0.5), tmp_path / "split", threading.Event())
    with zipfile.ZipFile(result["path"]) as archive:
        assert len(archive.namelist()) == 2
        archive.extractall(tmp_path / "parts")
    durations = [inspect(p)["duration"] for p in (tmp_path / "parts").iterdir()]
    assert all(d > 0 for d in durations)
    assert sum(durations) >= 1
