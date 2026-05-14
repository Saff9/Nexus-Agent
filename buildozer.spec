[app]
title = Nexus Agent
package.name = nexusagent
package.domain = io.nexus

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,md,json
source.exclude_exts = spec,pod,ps1,sh

version = 0.1.0
requirements = python3,kivy,httpx,pyyaml,prompt_toolkit,rich,openssl,sqlite3,certifi
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0

icon.filename = %(source.dir)s/icon.png
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.entrypoint = org.kivy.android.PythonActivity
android.app = org.kivy.android.PythonActivity

[buildozer]
log_level = 2
warn_on_root = 1
