#Requires -Version 5.1
param(
    [string]$HostPort = "8001",
    [string]$ContainerName = "qwen3-asr",
    [string]$Image = "qwenllm/qwen3-asr:latest",
    [string]$ContainerPort = "80",
    [string]$ModelName = "Qwen/Qwen3-ASR-1.7B",
    [string]$HfHomeHost = "",
    [string]$StartupTimeout = "600",
    [string]$VllmExtraArgs = "--enforce-eager"
)

if ([string]::IsNullOrEmpty($HfHomeHost)) {
    $HfHomeHost = Join-Path $env:USERPROFILE ".cache\huggingface"
}

$StartCommand = "vllm serve `"$ModelName`" --host 0.0.0.0 --port ${ContainerPort} ${VllmExtraArgs}"

function Test-PortInUse {
    param([int]$PortNumber)
    $connections = Get-NetTCPConnection -LocalPort $PortNumber -ErrorAction SilentlyContinue
    return ($connections -ne $null -and $connections.Count -gt 0)
}

function Test-ContainerRunning {
    param([string]$Name)
    $container = docker ps --format "{{.Names}}" 2>$null
    return ($container -match "^$Name$")
}

Write-Host "Note: qwenllm/qwen3-asr is a CUDA-based image." -ForegroundColor Yellow
Write-Host "It requires a Linux host with NVIDIA GPU support." -ForegroundColor Yellow

if (Test-PortInUse -PortNumber $HostPort) {
    Write-Host "Port $HostPort is already in use." -ForegroundColor Yellow
    if (Test-ContainerRunning -Name $ContainerName) {
        Write-Host "Qwen3-ASR container is already running." -ForegroundColor Green
        Write-Host "API base: http://127.0.0.1:${HostPort}/v1"
    } else {
        Write-Host "Another process is using port $HostPort. Stop it first or change HOST_PORT." -ForegroundColor Red
        exit 1
    }
    exit 0
}

if (-not (Test-Path $HfHomeHost)) {
    New-Item -ItemType Directory -Path $HfHomeHost -Force | Out-Null
}

Write-Host "Starting Qwen3-ASR container..." -ForegroundColor Cyan
Write-Host "  Image: $Image"
Write-Host "  Model: $ModelName"
Write-Host "  API base: http://127.0.0.1:${HostPort}/v1"
Write-Host "  HuggingFace cache: $HfHomeHost"
Write-Host "  Startup timeout: ${StartupTimeout}s"
Write-Host "  Start command: $StartCommand"

docker run -d `
    --name $ContainerName `
    --shm-size 16g `
    -p "${HostPort}:${ContainerPort}" `
    -v "${HfHomeHost}:/root/.cache/huggingface" `
    $Image `
    bash -lc "$StartCommand"

Write-Host "Waiting for Qwen3-ASR service to become ready..." -ForegroundColor Yellow
$timeout = [int]$StartupTimeout
$url = "http://127.0.0.1:${HostPort}/v1/models"
for ($i = 1; $i -le $timeout; $i++) {
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 1 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "Qwen3-ASR is ready!" -ForegroundColor Green
            Write-Host "  API base: http://127.0.0.1:${HostPort}/v1"
            Write-Host "  Transcriptions: http://127.0.0.1:${HostPort}/v1/audio/transcriptions"
            exit 0
        }
    } catch {
        # service not ready yet
    }
    Start-Sleep -Seconds 1
    if ($i % 60 -eq 0) {
        Write-Host "  ... still waiting ($i/${timeout}s)"
    }
}

Write-Host "Timed out waiting for Qwen3-ASR to start. Check logs:" -ForegroundColor Red
Write-Host "  docker logs ${ContainerName}"
exit 1