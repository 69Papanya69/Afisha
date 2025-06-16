#!/usr/bin/env pwsh
# Скрипт для административных задач в Docker-контейнерах

param (
    [Parameter(Position=0, Mandatory=$true)]
    [string]$command
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Администрирование myAfisha" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Show-Help {
    Write-Host "Доступные команды:" -ForegroundColor Yellow
    Write-Host "  createsuperuser  - Создать суперпользователя"
    Write-Host "  makemigrations   - Создать миграции"
    Write-Host "  migrate          - Применить миграции"
    Write-Host "  collectstatic    - Собрать статические файлы"
    Write-Host "  shell            - Запустить Django shell"
    Write-Host "  test             - Запустить тесты"
    Write-Host "  dbshell          - Запустить оболочку базы данных"
    Write-Host ""
    Write-Host "Примеры использования:" -ForegroundColor Yellow
    Write-Host "  ./scripts/docker-admin.ps1 createsuperuser"
    Write-Host "  ./scripts/docker-admin.ps1 test"
    exit 0
}

# Проверка наличия контейнеров
$containersRunning = docker-compose ps --services --filter "status=running" | Select-String "web"
if (-not $containersRunning) {
    Write-Host "✗ Контейнер web не запущен!" -ForegroundColor Red
    Write-Host "Запустите сначала контейнеры:" -ForegroundColor Yellow
    Write-Host "./scripts/docker-deploy.ps1" -ForegroundColor White
    exit 1
}

switch ($command) {
    "help" { 
        Show-Help 
    }
    "createsuperuser" {
        Write-Host "Создание суперпользователя Django..." -ForegroundColor Yellow
        docker-compose exec web python myAfisha/manage.py createsuperuser
    }
    "makemigrations" {
        Write-Host "Создание миграций..." -ForegroundColor Yellow
        docker-compose exec web python myAfisha/manage.py makemigrations
    }
    "migrate" {
        Write-Host "Применение миграций..." -ForegroundColor Yellow
        docker-compose exec web python myAfisha/manage.py migrate
    }
    "collectstatic" {
        Write-Host "Сборка статических файлов..." -ForegroundColor Yellow
        docker-compose exec web python myAfisha/manage.py collectstatic --noinput
    }
    "shell" {
        Write-Host "Запуск Django shell..." -ForegroundColor Yellow
        docker-compose exec web python myAfisha/manage.py shell
    }
    "test" {
        Write-Host "Запуск тестов..." -ForegroundColor Yellow
        docker-compose exec web python myAfisha/manage.py test
    }
    "dbshell" {
        Write-Host "Запуск оболочки базы данных..." -ForegroundColor Yellow
        docker-compose exec web python myAfisha/manage.py dbshell
    }
    default {
        Write-Host "✗ Неизвестная команда: $command" -ForegroundColor Red
        Show-Help
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Операция завершена" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green 
