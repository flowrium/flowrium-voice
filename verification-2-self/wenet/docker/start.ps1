#Requires -Version 5.1
param(
    [string]$Port = "10097",
    [string]$ContainerName = "wenet",
    [string]$Image = "mobvoiwenet/wenet:latest",
    [string]$StartupTimeout = "120",
    [string]$ModelDir = "/home/20210618_u2pp_conformer_libtorch",
    [string]$ChunkSize = "16"
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

Write-Host "Starting WeNet container..." -ForegroundColor Cyan
Write-Host "  Image: $Image"
Write-Host "  Port: $Port"
Write-Host "  Model dir: $ModelDir"
Write-Host "  Chunk size: $ChunkSize"
Write-Host "  Startup timeout: ${StartupTimeout}s"

if (Test-PortInUse -PortNumber $Port) {
    Write-Host "Port $Port is already in use." -ForegroundColor Yellow
    if (Test-ContainerRunning -Name $ContainerName) {
        Write-Host "WeNet container is already running." -ForegroundColor Green
        Write-Host "WebSocket: ws://localhost:$Port"
    } else {
        Write-Host "Another process is using port $Port. Stop it first or change the port." -ForegroundColor Red
        exit 1
    }
    exit 0
}

docker run -d `
    --name $ContainerName `
    -p "${Port}:${Port}" `
    $Image `
    bash -lc "export GLOG_logtostderr=1; /home/wenet/runtime/server/x86/build/websocket_server_main --port $Port --chunk_size $ChunkSize --model_path $ModelDir/final.zip --dict_path $ModelDir/words.txt"

Write-Host "Waiting for WeNet WebSocket to become ready..." -ForegroundColor Yellow
$timeout = [int]$StartupTimeout
for ($i = 1; $i -le $timeout; $i++) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.ConnectAsync("127.0.0.1", [int]$Port).Wait(1000) | Out-Null
        if ($client.Connected) {
            $client.Close()
            Write-Host "WeNet is ready!" -ForegroundColor Green
            Write-Host "  WebSocket: ws://localhost:$Port"
            exit 0
        }
        $client.Close()
    } catch {
        # port not ready yet
    }
    Start-Sleep -Seconds 1
    if ($i % 10 -eq 0) {
        Write-Host "  ... waiting ($i/${timeout}s)"
    }
}

Write-Host "Timed out waiting for WeNet to start. Check logs:" -ForegroundColor Red
Write-Host "  docker logs $ContainerName"
exit 1