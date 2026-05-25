#Requires -Version 5.1
<#
.SYNOPSIS
    Download Sherpa-ONNX quantized models for Windows.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File verification-3-edge/sherpa-onnx/setup/download_models.ps1
#>
$ErrorActionPreference = "Stop"
$SCRIPT_DIR = Split-Path -Parent $PSCommandPath
$ENGINE_DIR = Resolve-Path (Join-Path $SCRIPT_DIR "..")
$MODELS_DIR = Join-Path $ENGINE_DIR "models"

$MODELS = @(
    @{
        Name = "paraformer-zh-int8"
        Repo = "csukuangfj/sherpa-onnx-paraformer-zh-int8-2025-10-07"
        Files = @("model.int8.onnx", "tokens.txt")
    }
    @{
        Name = "sense-voice-zh-int8"
        Repo = "csukuangfj/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09"
        Files = @("model.int8.onnx", "tokens.txt")
    }
    @{
        Name = "zipformer-transducer-zh-int8"
        Repo = "csukuangfj/sherpa-onnx-streaming-zipformer-zh-int8-2025-06-30"
        Files = @("encoder.int8.onnx", "decoder.onnx", "joiner.int8.onnx", "tokens.txt")
    }
)

Write-Host "=== Downloading Sherpa-ONNX quantized models ===" -ForegroundColor Cyan
Write-Host "Models directory: $MODELS_DIR"
New-Item -ItemType Directory -Path $MODELS_DIR -Force | Out-Null

try {
    python -c "import huggingface_hub" 2>$null
} catch {
    Write-Host "huggingface_hub not installed. Run: pip install huggingface_hub" -ForegroundColor Red
    exit 1
}

foreach ($model in $MODELS) {
    $destDir = Join-Path $MODELS_DIR $model.Name
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null

    $allPresent = $true
    foreach ($file in $model.Files) {
        if (-not (Test-Path (Join-Path $destDir $file))) {
            $allPresent = $false
            break
        }
    }

    if ($allPresent) {
        Write-Host "  [$($model.Name)] Already exists, skipping." -ForegroundColor Green
        continue
    }

    Write-Host "  [$($model.Name)] Downloading from $($model.Repo) ..." -ForegroundColor Yellow
    python -c @"
from huggingface_hub import snapshot_download
snapshot_download('$($model.Repo)', local_dir=r'$destDir', ignore_patterns=['test_wavs/*'])
"@
    Write-Host "  [$($model.Name)] Done." -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Models downloaded ===" -ForegroundColor Cyan
Get-ChildItem -Path $MODELS_DIR -Recurse -Include "*.onnx", "tokens.txt" | Sort-Object FullName | ForEach-Object { Write-Host "  $($_.FullName)" }