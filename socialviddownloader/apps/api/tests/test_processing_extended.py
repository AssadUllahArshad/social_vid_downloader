import json
import subprocess
import threading
import zipfile
from pathlib import Path

import pytest

from app.media_errors import MediaError
from app.processing.engine import Options, inspect, process_files


@pytest.fixture(scope="module")
def media(tmp_path_factory):
    root = tmp_path_factory.mktemp("processing-extended")
    video = root / "video.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "testsrc=size=160x90:rate=10",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440",
            "-t",
            "2",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(video),
        ],
        check=True,
    )
    image = root / "image.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-frames:v", "1", str(image)], check=True)
    gif = root / "input.gif"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-an", "-vf", "fps=5,scale=160:-1", str(gif)], check=True)
    subtitle = root / "captions.srt"
    subtitle.write_text("1\n00:00:00,000 --> 00:00:01,500\nAuthorized test caption\n")
    embedded = root / "embedded.mkv"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(subtitle), "-map", "0", "-map", "1", "-c", "copy", str(embedded)],
        check=True,
    )
    silence = root / "silence.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "testsrc=size=160x90:rate=10",
            "-f",
            "lavfi",
            "-i",
            r"aevalsrc=if(lt(t\,1)\,0\,0.5*sin(2*PI*440*t)):s=44100",
            "-t",
            "2",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(silence),
        ],
        check=True,
    )
    return dict(video=video, image=image, gif=gif, subtitle=subtitle, embedded=embedded, silence=silence)


@pytest.mark.parametrize(
    "operation",
    [
        "splitter",
        "gif-to-video",
        "thumbnail",
        "thumbnail-grid",
        "images",
        "image-watermark",
        "text-watermark",
        "burn-subtitles",
        "extract-subtitles",
        "information",
        "filters",
        "stabilizer",
        "trim-silence",
        "storyboard",
    ],
)
def test_real_remaining_operations(operation, media, tmp_path):
    inputs = (
        [media["gif"]]
        if operation == "gif-to-video"
        else [media["image"], media["image"]]
        if operation == "images"
        else [media["video"], media["image"]]
        if operation == "image-watermark"
        else [media["video"], media["subtitle"]]
        if operation == "burn-subtitles"
        else [media["embedded"]]
        if operation == "extract-subtitles"
        else [media["silence"]]
        if operation == "trim-silence"
        else [media["video"]]
    )
    options = Options(
        width=160,
        height=90,
        frames=4,
        columns=2,
        segment_seconds=1,
        text="Safe: test 100% ' [text]",
        brightness=0.1,
        contrast=1.2,
        sharpen=0.5,
    )
    result = process_files(operation, inputs, options, tmp_path / "out", threading.Event())
    output = Path(result["path"])
    assert output.is_file() and output.stat().st_size == result["filesize"] > 0
    if operation == "splitter":
        with zipfile.ZipFile(output) as archive:
            assert len(archive.namelist()) == 2
            archive.extractall(tmp_path / "verified")
        for path in (tmp_path / "verified").iterdir():
            assert inspect(path)["duration"] > 0
    elif operation == "extract-subtitles":
        assert "Authorized test caption" in output.read_text()
    elif operation == "information":
        assert json.loads(output.read_text())["duration"] > 0
    else:
        measured = inspect(output)
        assert any(stream["codec_type"] == "video" for stream in measured["streams"])
        if operation == "trim-silence":
            assert measured["duration"] < 1.5
        if operation == "images":
            assert 3.8 <= measured["duration"] <= 4.2
    assert list(output.parent.iterdir()) == [output]


def test_missing_subtitles_fail_without_fake_output(media, tmp_path):
    with pytest.raises(MediaError) as failure:
        process_files("extract-subtitles", [media["video"]], Options(), tmp_path / "out", threading.Event())
    assert failure.value.code == "subtitles_unavailable"
    assert not (tmp_path / "out").exists()


def test_extreme_contact_sheet_is_rejected_before_encoding(media, tmp_path):
    with pytest.raises(MediaError) as failure:
        process_files("thumbnail-grid", [media["video"]], Options(width=1920, columns=8, frames=40), tmp_path / "out", threading.Event())
    assert failure.value.code == "grid_too_large"
    assert not (tmp_path / "out").exists()
