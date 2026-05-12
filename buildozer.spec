[app]

title = SovereignVideoStudio
package.name = sovereignstudio
package.domain = org.vishwakarma.sovereign

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,md

version = 1.0

requirements = python3,kivy,opencv,numpy,sqlite3,pillow

orientation = portrait

fullscreen = 0

android.permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

android.api = 31
android.minapi = 24
android.sdk = 31
android.ndk = 25b

android.archs = arm64-v8a

android.allow_backup = True

presplash.color = #000000

icon.filename = icon.png

log_level = 2

warn_on_root = 0

[buildozer]

log_level = 2

build_dir = .buildozer

bin_dir = bin
