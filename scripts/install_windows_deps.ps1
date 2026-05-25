#Requires -Version 5.1
<#
.SYNOPSIS
    Install all cross-platform Python dependencies for the Flowrium Voice project on Windows.
.DESCRIPTION
    Installs dependencies for: FunASR testing, edge-tts audio generation,
    Moonshine ASR, and Sherpa-ONNX ASR.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\install_windows_deps.ps1
#>
$ErrorActionPreference = "Stop"

Write-Host "=== Flowrium Voice - Windows Dependency Installer ===" -ForegroundColor Cyan
Write-Host ""

# 1. Core Python test dependencies
Write-Host "[1/5] Installing core testing dependencies..." -ForegroundColor Yellow
pip install websockets
Write-Host ""

# 2. edge-tts (audio generation)
Write-Host "[2/5] Installing edge-tts (TTS audio generation)..." -ForegroundColor Yellow
pip install edge-tts
Write-Host ""

# 3. Sherpa-ONNX (edge ASR engine)
Write-Host "[3/5] Installing Sherpa-ONNX..." -ForegroundColor Yellow
pip install sherpa-onnx
Write-Host ""

# 4. Moonshine (edge ASR engine)
Write-Host "[4/5] Installing Moonshine..." -ForegroundColor Yellow
pip install moonshine-voice soundfile
Write-Host ""

# 5. HuggingFace Hub (model downloads)
Write-Host "[5/5] Installing HuggingFace Hub..." -ForegroundColor Yellow
pip install huggingface_hub
Write-Host ""

Write-Host "=== Verification ===" -ForegroundColor Cyan
$packages = @("websockets", "edge_tts", "sherpa_onnx", "huggingface_hub")
foreach ($pkg in $packages) {
    python -c "import $pkg; v = getattr($pkg, '__version__', 'ok'); print(f'  $pkg: {v}')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  $pkg: FAILED" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Done! All Windows-compatible dependencies installed." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Generate audio:  python scripts/generate_school_audio.py"
Write-Host "  2. Run tests:       python verification-2-self/funasr/scripts/test_funasr_batch.py --mode 2pass --limit 5"