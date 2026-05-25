#Requires -Version 5.1
<#
.SYNOPSIS
    Install edge-tts for Windows TTS audio generation.
.DESCRIPTION
    Installs edge-tts Python package and verifies it works.
    Run this before using scripts/generate_school_audio.py on Windows.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\install_edge_tts.ps1
#>
Write-Host "=== Installing edge-tts ===" -ForegroundColor Cyan
Write-Host ""

pip install edge-tts
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install edge-tts." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Verifying installation ===" -ForegroundColor Cyan
python -c "import edge_tts; print('edge-tts installed successfully!')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Verification failed. The package may not be installed correctly." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Done! Now you can generate audio with:" -ForegroundColor Green
Write-Host "  python scripts/generate_school_audio.py" -ForegroundColor White