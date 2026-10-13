[app]

title = DEIN-K PERFORMANCE X
package.name = deinkperformancex
package.domain = org.deink
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json
version = 1.0.0

requirements = python3==3.12.10,hostpython3==3.12.10,kivy==2.3.1,kivymd==1.2.0,pyjnius

orientation = portrait
fullscreen = 0

android.api = 34
android.minapi = 26
android.ndk = 25b
android.archs = arm64-v8a

android.permissions = INTERNET,ACCESS_NETWORK_STATE,QUERY_ALL_PACKAGES,RECORD_AUDIO
android.accept_sdk_license = True
android.enable_androidx = True

android.numeric_version = 10000

[buildozer]

log_level = 2
warn_on_root = 1
