$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -3 -m venv .venv
}

$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"

& $Python -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) {
    throw "Failed to prepare pip, setuptools and wheel."
}

& $Python -m pip install -e "."
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install Mu into the build environment."
}

& $Python -m pip install pyinstaller
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install PyInstaller."
}

# Confirm the source application starts before packaging.
Write-Host "Environment prepared. Test the source application with:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\python.exe .\run.py" -ForegroundColor Cyan
Write-Host "Then build with:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean .\package\pyinstaller.spec" -ForegroundColor Cyan