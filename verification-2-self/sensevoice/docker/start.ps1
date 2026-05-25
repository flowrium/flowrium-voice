#Requires -Version 5.1
param(
    [string]$Port = "8000",
    [string]$ContainerName = "sensevoice",
    [string]$Image = "yiminger/sensevoice:latest",
    [string]$Language = "auto",
    [string]$StartupTimeout = "120"
)

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

if (Test-PortInUse -PortNumber $Port) {
    Write-Host "Port $Port is already in use." -ForegroundColor Yellow
    if (Test-ContainerRunning -Name $ContainerName) {
        Write-Host "SenseVoice container is already running." -ForegroundColor Green
        Write-Host "API: http://localhost:$Port"
        Write-Host "Docs: http://localhost:$Port/docs"
    } else {
        Write-Host "Another process is using port $Port. Stop it first or change the port." -ForegroundColor Red
        exit 1
    }
    exit 0
}

Write-Host "Starting SenseVoice container..." -ForegroundColor Cyan
Write-Host "  Image: $Image"
Write-Host "  Port: $Port"
Write-Host "  Language: $Language"
Write-Host "  Startup timeout: ${StartupTimeout}s"

docker run -d `
    --name $ContainerName `
    -p "${Port}:8000" `
    -e LANGUAGE="$Language" `
    $Image

Write-Host "Waiting for service to become ready..." -ForegroundColor Yellow
$timeout = [int]$StartupTimeout
for ($i = 1; $i -le $timeout; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/docs" -Method GET -TimeoutSec 1 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "SenseVoice is ready!" -ForegroundColor Green
            Write-Host "  API: http://localhost:$Port"
            Write-Host "  Docs: http://localhost:$Port/docs"
            exit 0
        }
    } catch {
        # service not ready yet
    }
    Start-Sleep -Seconds 1
    if ($i % 10 -eq 0) {
        Write-Host "  ... waiting ($i/${timeout}s)"
    }
}

Write-Host "Timed out waiting for SenseVoice to start. Check logs:" -ForegroundColor Red
Write-Host "  docker logs $ContainerName"
exit 1