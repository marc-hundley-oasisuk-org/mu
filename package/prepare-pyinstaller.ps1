param (
    [ValidateSet("Exam", "Teaching")]
    [string]$BuildProfile = "Exam"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

# Select the build-time editor assistance profile.
# The student import policy remains mandatory for every supported profile.
$env:MU_BUILD_PROFILE = $BuildProfile

$TeachingFeaturesEnabled = $BuildProfile -eq "Teaching"

Write-Host ""
Write-Host "Mu Build Configuration" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------"
Write-Host "Profile               : $BuildProfile"
Write-Host "Student Import Policy : Enabled (mandatory)"
Write-Host "Check                  : $(if ($TeachingFeaturesEnabled) { 'Enabled' } else { 'Disabled' })"
Write-Host "Tidy                   : $(if ($TeachingFeaturesEnabled) { 'Enabled' } else { 'Disabled' })"
Write-Host "Code Assistance        : $(if ($TeachingFeaturesEnabled) { 'Enabled' } else { 'Disabled' })"
Write-Host "------------------------------------------------------------"
Write-Host ""

try {
    if (-not (Test-Path ".venv\Scripts\python.exe")) {
        Write-Host "Creating repository virtual environment..." -ForegroundColor Cyan

        py -3 -m venv .venv

        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create the repository virtual environment."
        }
    }

    $Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"

    Write-Host "Preparing pip, setuptools and wheel..." -ForegroundColor Cyan

    & $Python -m pip install --upgrade pip setuptools wheel

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to prepare pip, setuptools and wheel."
    }

    Write-Host "Installing Mu into the build environment..." -ForegroundColor Cyan

    & $Python -m pip install -e "."

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install Mu into the build environment."
    }

    Write-Host "Ensuring PyInstaller is installed..." -ForegroundColor Cyan

    & $Python -m pip install pyinstaller

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install PyInstaller."
    }

    Write-Host ""
    Write-Host "Building Mu ($BuildProfile profile)..." -ForegroundColor Cyan

    & $Python -m PyInstaller `
        --noconfirm `
        --clean `
        .\package\pyinstaller.spec

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed."
    }

    $Executable = Join-Path $RepoRoot "dist\mu\mu.exe"

    if (-not (Test-Path $Executable)) {
        throw "PyInstaller completed but dist\mu\mu.exe was not found."
    }

    Write-Host ""
    Write-Host "Build completed successfully." -ForegroundColor Green
    Write-Host "Profile    : $BuildProfile" -ForegroundColor Green
    Write-Host "Executable : $Executable" -ForegroundColor Green
    Write-Host ""
    Write-Host "Validate the packaged application with:" -ForegroundColor Cyan
    Write-Host "  .\dist\mu\mu.exe" -ForegroundColor Cyan
}
finally {
    # The build profile is only build-time state. Do not leave it in the
    # administrator's PowerShell environment after packaging completes.
    Remove-Item Env:MU_BUILD_PROFILE -ErrorAction SilentlyContinue
}