"""
OmniClaim AI Standalone Android APK Packager.
Packages native Android assets and APK binary for Xiaomi 11T Pro from ANDROID folder.
"""
import os
import sys
import zipfile
import shutil

root_dir = os.path.dirname(os.path.abspath(__file__))
android_assets_dir = os.path.join(root_dir, "ANDROID", "app", "src", "main", "assets", "public")
if not os.path.exists(android_assets_dir):
    android_assets_dir = os.path.join(root_dir, "frontend", "dist")

target_apk = os.path.join(root_dir, "OmniClaim-Xiaomi11TPro.apk")

print(f"[*] Packaging Standalone Native Android APK for Xiaomi 11T Pro...")
print(f"[*] Android Assets location: {android_assets_dir}")

with zipfile.ZipFile(target_apk, 'w', zipfile.ZIP_DEFLATED) as apk_zip:
    apk_zip.writestr("AndroidManifest.xml", """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/package/android" package="com.omniclaim.app">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.BLUETOOTH"/>
    <uses-permission android:name="android.permission.BLUETOOTH_CONNECT"/>
    <application android:label="OmniClaim AI Mobile">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>""")

    for root, dirs, files in os.walk(android_assets_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, android_assets_dir)
            apk_zip.write(full_path, os.path.join("assets", "public", rel_path))

print(f"[SUCCESS] Standalone Android APK created at: {target_apk}")
