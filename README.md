# YouTube Downloader — Python/Kivy Android

تطبيق Kivy بسيط لتنزيل الفيديو بصيغة MP4 أو استخراج الصوت بصيغة MP3
باستخدام yt-dlp.

## مهم

استخدم التطبيق فقط لتنزيل محتوى تملكه، أو محتوى لديك إذن بتنزيله، أو محتوى
يوفر YouTube تنزيله بشكل قانوني. التطبيق لا يتجاوز DRM ولا يفتح الفيديوهات
الخاصة أو المدفوعة أو أي حماية وصول.

## الملفات

- `main.py`: واجهة التطبيق ومنطق التنزيل.
- `buildozer.spec`: إعداد بناء APK.
- `assets/ffmpeg`: ضع هنا ملف ffmpeg ثابتًا مبنيًا لـ Android ARM64.
- `assets/ffprobe`: ضع هنا ملف ffprobe ثابتًا مبنيًا لـ Android ARM64.

بدون ffmpeg/ffprobe:
- يمكن تنزيل MP4 المتاح كمسار واحد (progressive).
- استخراج MP3 ودمج أعلى جودات الفيديو/الصوت لن يعمل.

## بناء APK على Ubuntu / WSL2

ثبّت المتطلبات الأساسية (قد تختلف أسماء الحزم حسب إصدار Ubuntu):

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
    cmake libffi-dev libssl-dev automake
```

أنشئ بيئة Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install buildozer cython
```

ثم من داخل مجلد المشروع:

```bash
buildozer android debug
```

سيظهر ملف APK عادة داخل مجلد `bin/`.

## مكان الملفات على الهاتف

يستخدم التطبيق مجلد Android الخاص بالتطبيق، عادة بشكل قريب من:

`Android/data/com.example.pytubedownloader/files/Downloads`

هذا يتجنب طلب صلاحية وصول شاملة للتخزين في إصدارات Android الحديثة.

## ملاحظات تقنية

YouTube يغيّر آليات الاستخراج بشكل متكرر، لذلك يجب تحديث `yt-dlp` عند الحاجة.
بعض الفيديوهات قد تتطلب تسجيل دخول/كوكيز أو آليات إضافية، ولا يعني اسم التطبيق
أنه يستطيع تنزيل "كل" فيديو بلا استثناء.

## البناء تلقائيًا عبر GitHub Actions

تمت إضافة workflow في:

`.github/workflows/build-apk.yml`

بعد رفع المشروع إلى GitHub:

1. افتح تبويب **Actions**.
2. اختر **Build Android APK**.
3. اضغط **Run workflow** إذا لم يبدأ تلقائيًا.
4. بعد نجاح البناء، افتح نتيجة التشغيل.
5. من قسم **Artifacts** حمّل `youtube-downloader-apk`.

ملاحظة: استخراج MP3 ودمج أعلى جودة يحتاجان `ffmpeg` و`ffprobe` مبنيين لـ Android ARM64 داخل `assets/` قبل البناء.
