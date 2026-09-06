import os
import threading
import shutil
import stat
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

import yt_dlp


def is_android():
    try:
        from android import mActivity  # noqa
        return True
    except Exception:
        return False


def android_external_dir():
    """App-specific external folder; no broad storage permission is needed."""
    if not is_android():
        return str(Path.home() / "Downloads" / "PyTubeDownloader")

    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity
        base = activity.getExternalFilesDir(None).getAbsolutePath()
        out = os.path.join(base, "Downloads")
        os.makedirs(out, exist_ok=True)
        return out
    except Exception:
        return App.get_running_app().user_data_dir


def prepare_bundled_binary(name):
    """
    If assets/ffmpeg and assets/ffprobe are bundled, copy them to an executable
    location on first use. You must provide ARM64 Android static binaries.
    """
    app = App.get_running_app()
    src = os.path.join(os.path.dirname(__file__), "assets", name)

    if not os.path.isfile(src):
        return None

    dst = os.path.join(app.user_data_dir, name)
    try:
        if (not os.path.exists(dst)) or os.path.getsize(dst) != os.path.getsize(src):
            shutil.copy2(src, dst)
        mode = os.stat(dst).st_mode
        os.chmod(dst, mode | stat.S_IXUSR | stat.S_IXGRP)
        return dst
    except Exception:
        return None


class DownloaderUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10), padding=dp(14), **kwargs)

        self.add_widget(Label(
            text="YouTube Downloader",
            font_size="24sp",
            size_hint_y=None,
            height=dp(50)
        ))

        self.url_input = TextInput(
            hint_text="ألصق رابط YouTube هنا",
            multiline=False,
            size_hint_y=None,
            height=dp(52)
        )
        self.add_widget(self.url_input)

        row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))

        self.mode = Spinner(
            text="MP4 فيديو",
            values=("MP4 فيديو", "MP3 صوت"),
        )
        row.add_widget(self.mode)

        self.quality = Spinner(
            text="أفضل جودة",
            values=("أفضل جودة", "1080p", "720p", "480p", "360p"),
        )
        row.add_widget(self.quality)

        self.add_widget(row)

        self.download_btn = Button(
            text="تحميل",
            size_hint_y=None,
            height=dp(55)
        )
        self.download_btn.bind(on_release=self.start_download)
        self.add_widget(self.download_btn)

        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(24))
        self.add_widget(self.progress)

        self.status = Label(
            text="جاهز",
            halign="right",
            valign="middle"
        )
        self.status.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.add_widget(self.status)

        self.output_dir = android_external_dir()

    def set_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status, "text", text), 0)

    def set_progress(self, value):
        Clock.schedule_once(lambda dt: setattr(self.progress, "value", value), 0)

    def set_button(self, enabled):
        Clock.schedule_once(lambda dt: setattr(self.download_btn, "disabled", not enabled), 0)

    def progress_hook(self, data):
        status = data.get("status")
        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded = data.get("downloaded_bytes", 0)
            if total:
                pct = max(0, min(100, downloaded * 100 / total))
                self.set_progress(pct)
                self.set_status(f"جارٍ التحميل... {pct:.1f}%")
            else:
                self.set_status("جارٍ التحميل...")
        elif status == "finished":
            self.set_progress(100)
            self.set_status("اكتمل التنزيل، جارٍ تجهيز الملف...")

    def build_format(self):
        q = self.quality.text
        if self.mode.text == "MP3 صوت":
            return "bestaudio/best"

        if q == "أفضل جودة":
            # Prefer MP4-compatible tracks, then fall back to any best tracks.
            return (
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                "bestvideo+bestaudio/best[ext=mp4]/best"
            )

        height = q.replace("p", "")
        return (
            f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo[height<={height}]+bestaudio/"
            f"best[height<={height}][ext=mp4]/best[height<={height}]"
        )

    def start_download(self, *_):
        url = self.url_input.text.strip()
        if not url:
            self.set_status("أدخل رابطًا أولًا.")
            return

        self.set_button(False)
        self.set_progress(0)
        self.set_status("بدء التحميل...")
        threading.Thread(target=self.download_worker, args=(url,), daemon=True).start()

    def download_worker(self, url):
        os.makedirs(self.output_dir, exist_ok=True)

        ffmpeg_path = prepare_bundled_binary("ffmpeg")
        ffprobe_path = prepare_bundled_binary("ffprobe")

        ydl_opts = {
            "format": self.build_format(),
            "outtmpl": os.path.join(
                self.output_dir,
                "%(title).150B [%(id)s].%(ext)s"
            ),
            "progress_hooks": [self.progress_hook],
            "noplaylist": False,
            "windowsfilenames": True,
            "retries": 5,
            "fragment_retries": 5,
            "concurrent_fragment_downloads": 1,
            "quiet": True,
            "no_warnings": True,
        }

        if ffmpeg_path:
            # yt-dlp accepts the binary's directory here.
            ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_path)

        if self.mode.text == "MP3 صوت":
            if not (ffmpeg_path and ffprobe_path):
                self.set_status(
                    "MP3 يحتاج ffmpeg و ffprobe. ضع نسختي ARM64 Android داخل مجلد assets."
                )
                self.set_button(True)
                return

            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        else:
            # Merge to MP4 where possible. Requires ffmpeg when separate A/V streams are selected.
            if ffmpeg_path:
                ydl_opts["merge_output_format"] = "mp4"
            else:
                # Without ffmpeg, request a single progressive MP4 stream as fallback.
                q = self.quality.text
                if q == "أفضل جودة":
                    ydl_opts["format"] = "best[ext=mp4]/best"
                else:
                    h = q.replace("p", "")
                    ydl_opts["format"] = f"best[height<={h}][ext=mp4]/best[height<={h}]"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.set_progress(100)
            self.set_status(f"تم. الملفات محفوظة في:\n{self.output_dir}")
        except Exception as exc:
            msg = str(exc)
            if len(msg) > 500:
                msg = msg[-500:]
            self.set_status("فشل التحميل:\n" + msg)
        finally:
            self.set_button(True)


class YouTubeDownloaderApp(App):
    def build(self):
        self.title = "YouTube Downloader"
        return DownloaderUI()


if __name__ == "__main__":
    YouTubeDownloaderApp().run()
