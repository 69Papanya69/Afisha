#!/usr/bin/env pwsh
# Скрипт для просмотра логов Docker-контейнеров

param (
    [string]$service = "",
    [switch]$follow = $true,
    [int]$lines = 100
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Просмотр логов контейнеров myAfisha" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$dockerComposeCmd = "docker-compose logs"

if ($follow) {
    $dockerComposeCmd += " -f"
}

$dockerComposeCmd += " --tail=$lines"

if ($service) {
    Write-Host "Просмотр логов сервиса: $service" -ForegroundColor Yellow
    $dockerComposeCmd += " $service"
} else {
    Write-Host "Просмотр логов всех сервисов" -ForegroundColor Yellow
    Write-Host "Для просмотра логов определенного сервиса используйте:" -ForegroundColor Gray
    Write-Host "./scripts/docker-logs.ps1 -service web" -ForegroundColor Gray
    Write-Host "./scripts/docker-logs.ps1 -service celery_worker" -ForegroundColor Gray
    Write-Host "./scripts/docker-logs.ps1 -service celery_beat" -ForegroundColor Gray
}

Write-Host "`nДля выхода из просмотра логов нажмите Ctrl+C`n" -ForegroundColor Yellow

# Выполняем команду
Invoke-Expression $dockerComposeCmd 
