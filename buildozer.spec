[app]
title = Matrix ICT RFID Link
package.name = matrixictrfid
package.domain = com.matrixict.rfid
source.dir = .
source.include_exts = py,png,jpg,csv,db,jar,so
source.include_patterns = logo.png,icon.png,Matrix_Items.csv,reader.jar,libs/*,main.py
source.exclude_exts = spec,md,zip,yml,ipynb,txt
source.exclude_dirs = .git,bin,.buildozer,__pycache__,Matrix-ICT-APK-FINAL-V17,Matrix-ICT-Complete-Package,Matrix-ICT-Final-V14,github_build,.github,MATRIX-ICT-FIXED-FINAL
version = 0.17
requirements = python3,kivy,pyjnius
orientation = portrait
icon.filename = icon.png

# UHF Real - Chainway C72 - KEEP reader.jar
android.add_jars = reader.jar
android.add_src = libs
android.add_aars =

[buildozer]
log_level = 1
warn_on_root = 0

[app:android]
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license_agreement = True
android.archs = arm64-v8a
android.allow_backup = False
p4a.bootstrap = sdl2
p4a.branch = master
