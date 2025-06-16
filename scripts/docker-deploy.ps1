#!/usr/bin/env pwsh
# Скрипт для полного развертывания проекта в Docker

# Вывод заголовка
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Развертывание myAfisha в Docker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка установки Docker
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker установлен: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker не установлен или не запущен!" -ForegroundColor Red
    Write-Host "Установите Docker Desktop с сайта: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Проверка установки Docker Compose
try {
    $dockerComposeVersion = docker-compose --version
    Write-Host "✓ Docker Compose установлен: $dockerComposeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Compose не установлен!" -ForegroundColor Red
    exit 1
}

Write-Host "`nШаг 1: Сборка контейнеров..." -ForegroundColor Cyan
docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Ошибка при сборке контейнеров!" -ForegroundColor Red
    exit 1
}

Write-Host "`nШаг 2: Запуск контейнеров..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Ошибка при запуске контейнеров!" -ForegroundColor Red
    exit 1
}

# Небольшая пауза для запуска контейнеров
Write-Host "`nОжидание запуска контейнеров..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "`nШаг 3: Применение миграций..." -ForegroundColor Cyan
docker-compose exec -T web python myAfisha/manage.py migrate

Write-Host "`nШаг 4: Сборка статических файлов..." -ForegroundColor Cyan
docker-compose exec -T web python myAfisha/manage.py collectstatic --noinput

Write-Host "`nШаг 5: Проверка статуса контейнеров..." -ForegroundColor Cyan
docker-compose ps

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Развертывание завершено успешно!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Доступные сервисы:" -ForegroundColor Cyan
Write-Host "- Django: http://localhost:8000/" -ForegroundColor White
Write-Host "- Django Admin: http://localhost:8000/admin/" -ForegroundColor White
Write-Host "- Django Silk: http://localhost:8000/silk/" -ForegroundColor White
Write-Host "- Flower (мониторинг Celery): http://localhost:5555/" -ForegroundColor White
Write-Host ""
Write-Host "Для создания суперпользователя выполните:" -ForegroundColor Yellow
Write-Host "./scripts/docker-admin.ps1 createsuperuser" -ForegroundColor White
Write-Host "" 
