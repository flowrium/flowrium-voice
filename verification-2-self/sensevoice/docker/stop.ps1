param([string]$ContainerName = "sensevoice")
$running = docker ps --format "{{.Names}}" 2>$null
if ($running -match "^$ContainerName$") {
    Write-Host "Stopping SenseVoice container..." -ForegroundColor Yellow
    docker stop $ContainerName
    docker rm $ContainerName
    Write-Host "SenseVoice container stopped and removed." -ForegroundColor Green
} else {
    Write-Host "No running SenseVoice container found." -ForegroundColor Gray
}