import subprocess
import os
import glob
import shutil

import yt_dlp


def _find_ffmpeg():
    if shutil.which("ffmpeg"):
        return shutil.which("ffmpeg")
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


class AudioExtractor:
    def __init__(self, ffmpeg_path=None):
        self.ffmpeg_path = ffmpeg_path or _find_ffmpeg()

    def extract_from_file(self, input_path, output_path):
        cmd = [
            self.ffmpeg_path,
            "-i", input_path,
            "-vn",
            "-acodec", "libmp3lame",
            "-ab", "192k",
            "-ar", "44100",
            "-y",
            output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def extract_from_url(self, url, output_dir, progress_callback=None, browser="chrome", cookies_file=None):
        def progress_hook(d):
            if d["status"] == "downloading" and progress_callback:
                pct = d.get("_percent_str", "N/A")
                progress_callback(f"Загрузка: {pct}")
            elif d["status"] == "finished" and progress_callback:
                progress_callback("Конвертация...")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "quiet": True,
            "no_warnings": True,
        }

        if cookies_file and os.path.exists(cookies_file):
            ydl_opts["cookiefile"] = cookies_file
        else:
            ydl_opts["cookiesfrombrowser"] = (browser,)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "output")
            tmp_file = os.path.join(output_dir, f"{title}.{info.get('ext', 'webm')}")

        if not os.path.exists(tmp_file):
            patterns = glob.glob(os.path.join(output_dir, f"{title}.*"))
            if patterns:
                tmp_file = patterns[0]
            else:
                raise FileNotFoundError("Downloaded file not found")

        output_path = os.path.join(output_dir, f"{title}.mp3")
        cmd = [
            self.ffmpeg_path,
            "-i", tmp_file,
            "-vn",
            "-acodec", "libmp3lame",
            "-ab", "192k",
            "-ar", "44100",
            "-y",
            output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        if tmp_file != output_path and os.path.exists(tmp_file):
            os.remove(tmp_file)

        return output_path
