[app]
title = YouTube Downloader
package.name = pytubedownloader
package.domain = com.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,bin
source.include_patterns = assets/*
version = 1.0.0

requirements = python3,kivy,yt-dlp,pyjnius

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 35
android.minapi = 24
android.archs = arm64-v8a

# If you add ARM64 Android ffmpeg/ffprobe executables in assets/,
# they are included by source.include_patterns above.

[buildozer]
log_level = 2
warn_on_root = 1
