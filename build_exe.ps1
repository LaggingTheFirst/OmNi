# Build script for creating OmNi executable
# Run this script to generate the standalone executable

# Install PyInstaller if not already installed
pip install pyinstaller

# Clean previous builds
if (Test-Path "dist") { Remove-Item -Recurse "dist" -Force }
if (Test-Path "build") { Remove-Item -Recurse "build" -Force }

# Build the executable using the spec file
python -m PyInstaller omni.spec

Write-Host ""
Write-Host '✓ Build complete!' -ForegroundColor Green
Write-Host 'Executable location: dist\OmNi.exe' -ForegroundColor Yellow
Write-Host ""
Write-Host 'Config file will be stored at:' -ForegroundColor Cyan
Write-Host '%APPDATA%\OmNi\config.py' -ForegroundColor Yellow
Write-Host ""
Write-Host 'To run: .\dist\OmNi.exe' -ForegroundColor Cyan
