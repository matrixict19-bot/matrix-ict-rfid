[app]
title = Matrix ICT RFID Link
package.name = matrixictrfid
package.domain = com.matrixict.rfid
source.dir = .
source.include_exts = py,png,jpg,csv,db,jar,so
source.include_patterns = main.py,reader.jar,icon.png,logo.png,libs/*
source.exclude_exts = spec,md,zip,yml,ipynb,txt
source.exclude_dirs = .git,bin,.buildozer,__pycache__,.github
version = 0.18
requirements = python3,kivy==2.3.1,pyjnius
orientation = portrait
icon.filename = icon.png

# UHF - GXWL GClient SDK (reader.jar) + native serial libs taken from the G2 UHF demo APK
android.add_jars = reader.jar
android.add_libs_arm64_v8a = libs/arm64-v8a/*.so
android.add_libs_armeabi_v7a = libs/armeabi-v7a/*.so

[buildozer]
log_level = 2
warn_on_root = 0

[app:android]
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 28c
android.accept_sdk_license_agreement = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = False
android.ant_path = /home/runner/.buildozer/android/platform/apache-ant-1.9.4/bin
p4a.bootstrap = sdl2
p4a.branch = master
