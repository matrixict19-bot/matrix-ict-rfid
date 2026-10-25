[app]
title = Matrix ICT RFID Link
package.name = matrixictrfid
package.domain = com.matrixict.rfid
source.dir = .
source.include_exts = py,png,csv,db
source.include_patterns = logo.png,icon.png,Matrix_Items.csv
version = 0.17
requirements = python3==3.11.6,kivy==2.3.0,hostpython3==3.11.6
orientation = portrait
icon.filename = icon.png

[buildozer]
log_level = 2
warn_on_root = 0

[app:android]
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license_agreement = True
android.archs = arm64-v8a
p4a.bootstrap = sdl2
p4a.branch = master
