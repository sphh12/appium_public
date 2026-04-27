Param(
  [switch]$SkipEmulator,
  [switch]$SkipAllure,
  [string]$AndroidPlatformVersion = ""
)

$ErrorActionPreference = 'Stop'

Write-Host "========================================"
Write-Host "  Appium Project Bootstrap (Windows)"
Write-Host "========================================"

Set-Location (Split-Path -Parent $PSScriptRoot)

if ($AndroidPlatformVersion -ne "") {
  $env:ANDROID_PLATFORM_VERSION = $AndroidPlatformVersion
  Write-Host "[ENV] ANDROID_PLATFORM_VERSION=$AndroidPlatformVersion"
}

Write-Host "[1/5] Checking tools..."
foreach ($cmd in @('python','npm')) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    throw "Missing command in PATH: $cmd"
  }
}

Write-Host "[2/5] Python venv + requirements..."
if (-not (Test-Path .\venv)) {
  python -m venv venv
}
. .\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "[3/5] Node dependencies (local appium + allure)..."
npm install --no-audit --no-fund

Write-Host "[4/5] Appium driver: UiAutomator2..."
# Use local appium via npx
npx --yes appium driver install uiautomator2 | Out-Host

if (-not $SkipEmulator) {
  Write-Host "[5/5] ADB/Emulator quick check..."
  if (Get-Command adb -ErrorAction SilentlyContinue) {
    adb start-server | Out-Host
    adb devices -l | Out-Host
  } else {
    Write-Host "adb not found in PATH (Android SDK not configured)"
  }
}

if (-not $SkipAllure) {
  Write-Host "Allure check (local):"
  npx --yes allure --version | Out-Host
}

Write-Host ""
Write-Host "Bootstrap complete."
Write-Host "Run tests: ./shell/run-app.sh"
