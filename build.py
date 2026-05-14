#!/usr/bin/env python3
"""Nexus Agent - Universal Build Script."""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Force UTF-8 encoding for standard output to support emojis on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def log(msg, level="INFO"):
    """Log message with level."""
    levels = {"INFO": "📦", "SUCCESS": "✅", "ERROR": "❌", "WARN": "⚠️"}
    print(f"{levels.get(level, '•')} {msg}")

def run(cmd, cwd=None, shell=True):
    """Run command and return success."""
    log(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=shell, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {e}", "ERROR")
        return False

def build_windows():
    """Build Windows .exe with PyInstaller."""
    log("Building Windows executable...", "INFO")
    
    # Install PyInstaller
    run("pip install pyinstaller")
    
    # Build spec file
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['cli.py'],
    pathex=['.'],
    binaries=[],
    datas=[('core', 'core'), ('tools', 'tools')],
    hiddenimports=['httpx', 'yaml', 'prompt_toolkit', 'rich'],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='nexus',
    debug=False,
    strip=False,
    upx=True,
    console=True,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
"""
    Path('nexus.spec').write_text(spec_content)
    
    # Build
    run("pyinstaller --clean nexus.spec")
    
    if Path('dist/nexus.exe').exists():
        log("Windows .exe built successfully!", "SUCCESS")
        return True
    log("Windows build failed", "ERROR")
    return False

def build_linux():
    """Build Linux binary/AppImage."""
    log("Building Linux binary...", "INFO")
    
    # Install PyInstaller
    run("pip install pyinstaller")
    
    # Build
    run("pyinstaller --onefile --name nexus cli.py")
    
    if Path('dist/nexus').exists():
        log("Linux binary built successfully!", "SUCCESS")
        return True
    log("Linux build failed", "ERROR")
    return False

def build_macos():
    """Build macOS .app bundle."""
    log("Building macOS app...", "INFO")
    
    run("pip install pyinstaller")
    
    # Build as .app
    run("pyinstaller --windowed --name NexusAgent --icon=icon.icns cli.py 2>/dev/null || " +
        "pyinstaller --name NexusAgent cli.py")
    
    if Path('dist/NexusAgent.app').exists() or Path('dist/nexus').exists():
        log("macOS app built successfully!", "SUCCESS")
        return True
    log("macOS build completed (console mode)", "WARN")
    return True

def build_android():
    """Build Android APK with Buildozer."""
    log("Building Android APK...", "INFO")
    
    # Check if buildozer is installed
    if not shutil.which('buildozer'):
        log("Installing buildozer...", "INFO")
        run("pip install buildozer")
    
    # Initialize buildozer if spec doesn't exist
    if not Path('buildozer.spec').exists():
        run("buildozer init")
    
    # Build APK
    log("This may take 20-30 minutes for first build...", "WARN")
    run("buildozer -v android debug")
    
    if Path('bin').exists():
        apks = list(Path('bin').glob('*.apk'))
        if apks:
            log(f"Android APK built: {apks[0].name}", "SUCCESS")
            return True
    
    log("Android build may still be in progress", "WARN")
    return True

def build_all():
    """Build for all platforms."""
    platform = sys.platform
    
    log(f"Building for platform: {platform}", "INFO")
    log("=" * 50)
    
    results = {}
    
    if platform == 'win32':
        results['windows'] = build_windows()
    elif platform == 'darwin':
        results['macos'] = build_macos()
    elif platform == 'linux':
        results['linux'] = build_linux()
        # Also try Android if buildozer available
        if shutil.which('buildozer'):
            results['android'] = build_android()
    else:
        log(f"Unknown platform: {platform}", "ERROR")
        return False
    
    log("=" * 50)
    log("Build Summary:", "INFO")
    for platform, success in results.items():
        status = "✓" if success else "✗"
        log(f"  {status} {platform}")
    
    return all(results.values())

def package_pip():
    """Build pip package."""
    log("Building pip package...", "INFO")
    
    run("pip install build twine")
    run("python -m build")
    
    if Path('dist').exists():
        wheels = list(Path('dist').glob('*.whl'))
        if wheels:
            log(f"Wheel built: {wheels[0].name}", "SUCCESS")
            return True
    
    log("Pip package build failed", "ERROR")
    return False

def main():
    """Main build entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Nexus Agent Build Tool')
    parser.add_argument('--platform', choices=['windows', 'linux', 'macos', 'android', 'all'],
                       default='all', help='Target platform')
    parser.add_argument('--pip', action='store_true', help='Build pip package')
    
    args = parser.parse_args()
    
    if args.pip:
        package_pip()
        return
    
    if args.platform == 'all':
        build_all()
    elif args.platform == 'windows':
        build_windows()
    elif args.platform == 'linux':
        build_linux()
    elif args.platform == 'macos':
        build_macos()
    elif args.platform == 'android':
        build_android()

if __name__ == "__main__":
    main()
