param([string]$ContainerName = "qwen3-asr")
$running = docker ps --format "{{.Names}}" 2>$null
if ($running -match "^$ContainerName$") {
    Write-Host "Stopping Qwen3-ASR container..." -ForegroundColor Yellow
    docker stop $ContainerName
    docker rm $ContainerName
    Write-Host "Qwen3-ASR container stopped and removed." -ForegroundColor Green
} else {
    Write-Host "No running Qwen3-ASR container found." -ForegroundColor Gray
}