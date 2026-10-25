[app]
title = Matrix ICT RFID Link
package.name = matrixictrfid
package.domain = com.matrixict.rfid
source.dir = .
source.include_exts = py,png,csv,db,jar,so
source.include_patterns = logo.png,icon.png,Matrix_Items.csv,libs/*,reader.jar,03_Libs_UHF_C72/*
source.exclude_patterns = buildozer.*,*.zip,*.pdf,*.md
version = 0.17
requirements = python3==3.11.6,kivy==2.3.0,pyjnius,hostpython3==3.11.6
orientation = portrait
icon.filename = icon.png
fullscreen = 0

# UHF Real - Chainway C72
android.add_jars = reader.jar
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA,VIBRATE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license_agreement = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = False

[buildozer]
log_level = 2
warn_on_root = 0

[app:android]
p4a.bootstrap = sdl2
p4a.branch = master
# شيل local_recipes لو مش عندك فولدر p4a-recipes على GitHub
# p4a.local_recipes = ./p4a-recipes
