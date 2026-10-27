# MATRIX ICT RFID - V29 CLEAN UPLOAD

## Structure - No Confusion
- main.py -> V28 REAL JAR + Barcode Close Fix
- .github/workflows/build.yml -> V29 Flex Path
- reader.jar (779KB) + SDK_Release_v202207131954.jar -> Real C72 SDK
- arm64-v8a/ + armeabi-v7a/ -> libSerialPort.so

Upload ALL files as they are to GitHub root.

## How to upload
1. Delete everything in your repo EXCEPT .git (keep hidden)
2. Upload all files from this zip keeping folder structure
3. Commit -> Run workflow -> Check log: should say "UHF SDK FOUND"

## What was fixed V29
- Barcode: force_disable() in RFID screen - closes 3 times, blocks open
- UHF: Real reader.jar 779KB - no more Fake mode
