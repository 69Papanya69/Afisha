#!/usr/bin/env pwsh
# Скрипт для остановки и удаления контейнеров Docker

param (
    [switch]$removeVolumes = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Остановка контейнеров myAfisha" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($removeVolumes) {
    Write-Host "Остановка и удаление контейнеров вместе с томами..." -ForegroundColor Yellow
    docker-compose down -v
} else {
    Write-Host "Остановка и удаление контейнеров (без томов)..." -ForegroundColor Cyan
    docker-compose down
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Ошибка при остановке контейнеров!" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Контейнеры успешно остановлены!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`nДля запуска контейнеров снова выполните:" -ForegroundColor Yellow
Write-Host "./scripts/docker-deploy.ps1" -ForegroundColor White
Write-Host "" 
