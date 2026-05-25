#Requires -Version 5.1
<#
.SYNOPSIS
    Download Moonshine models for Windows.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File verification-3-edge/moonshine/setup/download_models.ps1
#>
$ErrorActionPreference = "Stop"
$SCRIPT_DIR = Split-Path -Parent $PSCommandPath
$ENGINE_DIR = Resolve-Path (Join-Path $SCRIPT_DIR "..")
$MODELS_DIR = Join-Path $ENGINE_DIR "models"
$CACHE_DIR = Join-Path $ENGINE_DIR "cache"
$METADATA_DIR = Join-Path $MODELS_DIR "metadata"

Write-Host "=== Downloading Moonshine models ===" -ForegroundColor Cyan
New-Item -ItemType Directory -Path $MODELS_DIR -Force | Out-Null
New-Item -ItemType Directory -Path $METADATA_DIR -Force | Out-Null

$env:XDG_CACHE_HOME = $CACHE_DIR

function Download-MoonshineModel {
    param([string]$ModelName, [string]$Language)

    $outputDir = Join-Path $MODELS_DIR $ModelName
    $hasModel = (Get-ChildItem -Path $outputDir -Include "*.onnx", "*.bin" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1) -ne $null

    if ($hasModel) {
        Write-Host "  [$ModelName] already exists, skipping." -ForegroundColor Green
        return
    }

    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "  [$ModelName] downloading ..." -ForegroundColor Yellow

    $metadataPath = Join-Path $METADATA_DIR "$ModelName.json"
    $pyCode = @"
import json, shutil, sys
from pathlib import Path
from moonshine_voice import get_model_for_language

language = sys.argv[1]
output_dir = Path(sys.argv[2])
metadata_path = Path(sys.argv[3])
model_path, model_arch = get_model_for_language(language, None)
model_path = Path(model_path)
target_path = output_dir / model_path.name
if not target_path.exists():
    shutil.copy2(model_path, target_path)
metadata_path.write_text(
    json.dumps({
        'language': language,
        'source_model_path': str(model_path),
        'copied_model_path': str(target_path),
        'model_arch': model_arch,
    }, ensure_ascii=False, indent=2),
    encoding='utf-8',
)
print(target_path)
"@

    python -c $pyCode $Language $outputDir $metadataPath
    Write-Host "  [$ModelName] Done." -ForegroundColor Green
}

Download-MoonshineModel -ModelName "zh" -Language "zh"
Download-MoonshineModel -ModelName "en" -Language "en"

Write-Host ""
Write-Host "=== Models ready ===" -ForegroundColor Cyan
Get-ChildItem -Path $MODELS_DIR -Recurse -Include "*.onnx", "*.bin", "*.json" | Sort-Object FullName | ForEach-Object { Write-Host "  $($_.FullName)" }