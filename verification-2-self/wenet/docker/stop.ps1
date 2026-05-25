param([string]$ContainerName = "wenet")
$running = docker ps --format "{{.Names}}" 2>$null
if ($running -match "^$ContainerName$") {
    Write-Host "Stopping WeNet container..." -ForegroundColor Yellow
    docker stop $ContainerName
    docker rm $ContainerName
    Write-Host "WeNet container stopped and removed." -ForegroundColor Green
} else {
    Write-Host "No running WeNet container found." -ForegroundColor Gray
}