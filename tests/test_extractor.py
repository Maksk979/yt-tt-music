import os
import subprocess
import tempfile
import pytest
from core.extractor import AudioExtractor


def _create_test_video(path, ffmpeg_path, duration=1):
    cmd = [
        ffmpeg_path, "-y",
        "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}",
        "-f", "lavfi", "-i", f"color=c=black:s=320x240:d={duration}",
        "-shortest",
        "-c:v", "libx264", "-c:a", "aac",
        path,
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def test_extract_from_file_returns_mp3_path():
    extractor = AudioExtractor()
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, "test_video.mp4")
        _create_test_video(video_path, extractor.ffmpeg_path)
        output_path = os.path.join(tmpdir, "output.mp3")
        result = extractor.extract_from_file(video_path, output_path)
        assert result == output_path
        assert os.path.exists(result)
        assert os.path.getsize(output_path) > 0


def test_extract_from_url_returns_mp3_path():
    extractor = AudioExtractor()
    with tempfile.TemporaryDirectory() as tmpdir:
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = extractor.extract_from_url(url, tmpdir)
        assert result.endswith(".mp3")
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0
