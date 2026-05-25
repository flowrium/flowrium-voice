param(
    [string]$HostAddr = "127.0.0.1",
    [string]$Port = "18081",
    [string]$WsUrl = $env:WENET_WS_URL
)

if ([string]::IsNullOrEmpty($WsUrl)) {
    $WsUrl = "ws://127.0.0.1:10097"
}

Write-Host "Starting WeNet demo server..." -ForegroundColor Cyan
Write-Host "  Demo: http://${HostAddr}:${Port}"
Write-Host "  Proxy WebSocket: ws://${HostAddr}:$($Port + 1)"
Write-Host "  Upstream WeNet: ${WsUrl}"

$scriptDir = Split-Path -Parent $PSCommandPath
python "$scriptDir/serve.py" --host $HostAddr --port $Port --ws-url $WsUrl