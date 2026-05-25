param(
    [string]$HostAddr = "127.0.0.1",
    [string]$Port = "18080",
    [string]$ApiUrl = $env:SENSEVOICE_API_URL
)

if ([string]::IsNullOrEmpty($ApiUrl)) {
    $ApiUrl = "http://127.0.0.1:8000"
}

Write-Host "Starting SenseVoice demo server..." -ForegroundColor Cyan
Write-Host "  Demo: http://${HostAddr}:${Port}"
Write-Host "  Proxy target: ${ApiUrl}"

$scriptDir = Split-Path -Parent $PSCommandPath
python "$scriptDir/serve.py" --host $HostAddr --port $Port --api-url $ApiUrl