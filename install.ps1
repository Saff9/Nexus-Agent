# Nexus Agent Installer for Windows
# Run in PowerShell: irm <url> | iex

Write-Host "╔═══════════════════════════════════════════════════════╗"
Write-Host "║                                                       ║"
Write-Host "║   ⚡  N E X U S   A G E N T   I N S T A L L E R       ║"
Write-Host "║               (Windows)                               ║"
Write-Host "║                                                       ║"
Write-Host "╚═══════════════════════════════════════════════════════╝"
Write-Host ""

# Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Host "❌ Python 3.10+ is required" -ForegroundColor Red
    Write-Host "   Download from: https://python.org/downloads"
    Write-Host "   Make sure to check 'Add Python to PATH' during installation"
    exit 1
}

$pythonVersion = & $pythonCmd --version
Write-Host "✓ Python: $pythonVersion"

# Set install directory
$installDir = if ($env:NEXUS_INSTALL_DIR) { $env:NEXUS_INSTALL_DIR } else { "$env:USERPROFILE\.nexus" }
$binDir = "$env:USERPROFILE\.local\bin"

Write-Host "📁 Install directory: $installDir"

# Create directories
New-Item -ItemType Directory -Force -Path $installDir | Out-Null
New-Item -ItemType Directory -Force -Path $binDir | Out-Null

# Clone or copy repository
Write-Host "📦 Installing..."
$srcDir = "$installDir\src"

if (Test-Path "nexus-agent") {
    Copy-Item -Recurse -Force "nexus-agent\*" $installDir
} else {
    # Try git clone
    try {
        git clone "https://github.com/yourusername/nexus-agent.git" $srcDir 2>$null
    } catch {
        Write-Host "⚠️  Git not available, using local files" -ForegroundColor Yellow
        New-Item -ItemType Directory -Force -Path $srcDir | Out-Null
        Copy-Item -Recurse -Force ".\*" $srcDir 2>$null
    }
}

# Create virtual environment
Write-Host "🔧 Creating virtual environment..."
& $pythonCmd -m venv "$installDir\venv"

# Activate venv
$venvPython = "$installDir\venv\Scripts\python.exe"
$venvPip = "$installDir\venv\Scripts\pip.exe"

# Install dependencies
Write-Host "📦 Installing dependencies..."
& $venvPip install --upgrade pip
& $venvPip install httpx pyyaml prompt-toolkit rich

# Install nexus-agent
Set-Location $installDir\src
& $venvPip install -e .

# Create launcher
$launcherScript = @"
@echo off
set NEXUS_INSTALL_DIR=%NEXUS_INSTALL_DIR:%USERPROFILE%=%USERPROFILE%
call "%NEXUS_INSTALL_DIR%\venv\Scripts\activate.bat"
python "%NEXUS_INSTALL_DIR%\src\cli.py" %*
"@

$launcherPath = "$binDir\nexus.bat"
$launcherScript | Out-File -FilePath $launcherPath -Encoding ascii

# Add to PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$binDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$binDir", "User")
    Write-Host ""
    Write-Host "⚠️  PATH updated. Please restart PowerShell for changes to take effect." -ForegroundColor Yellow
}

# Build .exe with PyInstaller (optional)
Write-Host ""
Write-Host "📦 Building standalone .exe..." -ForegroundColor Cyan
& $venvPip install pyinstaller

$pyinstallerSpec = @"
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['cli.py'],
    pathex=['$installDir\\src'],
    binaries=[],
    datas=[
        ('$installDir\\src\\core', 'core'),
        ('$installDir\\src\\tools', 'tools'),
    ],
    hiddenimports=[
        'httpx',
        'yaml',
        'prompt_toolkit',
        'rich',
    ],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='nexus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"@

$pyinstallerSpec | Out-File -FilePath "$installDir\nexus.spec" -Encoding ascii

Set-Location $installDir
& "$installDir\venv\Scripts\pyinstaller.exe" --clean nexus.spec

# Copy exe to bin directory
if (Test-Path "$installDir\dist\nexus.exe") {
    Copy-Item "$installDir\dist\nexus.exe" "$binDir\nexus.exe"
    Write-Host "✓ Built: $binDir\nexus.exe" -ForegroundColor Green
}

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════╗"
Write-Host "║                                                       ║"
Write-Host "║   ⚡  I N S T A L L A T I O N   C O M P L E T E       ║"
Write-Host "║                                                       ║"
Write-Host "╚═══════════════════════════════════════════════════════╝"
Write-Host ""
Write-Host "🚀 Quick Start:" -ForegroundColor Green
Write-Host "   nexus              # Start interactive CLI"
Write-Host "   nexus.exe          # Run standalone .exe"
Write-Host ""
Write-Host "⚙️  Configure API keys (PowerShell):" -ForegroundColor Yellow
Write-Host '   $env:OPENAI_API_KEY="your-key"'
Write-Host '   [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-key", "User")'
Write-Host ""
Write-Host "📚 Documentation: https://nexus-agent.io/docs"
Write-Host ""

Set-Location $PSScriptRoot
