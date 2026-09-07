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
android.ndk = 28c
android.archs = arm64-v8a


[buildozer]

log_level = 2
warn_on_root = 1
