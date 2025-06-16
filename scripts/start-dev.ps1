#!/usr/bin/env pwsh
# Скрипт для запуска проекта в режиме разработки (без Docker)

param(
    [switch]$noMigrations = $false,
    [switch]$noStatic = $false
)

# Настройка виртуальной среды
$pythonCmd = "python"
$venvPath = ".venv"
$activateScript = "$venvPath\Scripts\Activate.ps1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Запуск myAfisha (режим разработки)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка наличия виртуальной среды
if (-not (Test-Path $venvPath)) {
    Write-Host "Создание виртуальной среды..." -ForegroundColor Yellow
    & $pythonCmd -m venv $venvPath
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Ошибка создания виртуальной среды!" -ForegroundColor Red
        exit 1
    }
}

# Активация виртуальной среды
Write-Host "Активация виртуальной среды..." -ForegroundColor Yellow
try {
    & $activateScript
} catch {
    Write-Host "✗ Ошибка активации виртуальной среды!" -ForegroundColor Red
    Write-Host $_ -ForegroundColor Red
    exit 1
}

# Установка зависимостей
Write-Host "`nУстановка зависимостей..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Ошибка установки зависимостей!" -ForegroundColor Red
    exit 1
}

# Применение миграций, если нужно
if (-not $noMigrations) {
    Write-Host "`nПрименение миграций..." -ForegroundColor Yellow
    python myAfisha/manage.py migrate
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Ошибка при применении миграций!" -ForegroundColor Red
        exit 1
    }
}

# Сборка статических файлов, если нужно
if (-not $noStatic) {
    Write-Host "`nСборка статических файлов..." -ForegroundColor Yellow
    python myAfisha/manage.py collectstatic --noinput
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Ошибка при сборке статических файлов!" -ForegroundColor Red
        exit 1
    }
}

# Запуск Redis (если установлен)
Write-Host "`nПроверка Redis..." -ForegroundColor Yellow
$redisRunning = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue

if (-not $redisRunning) {
    Write-Host "Redis не запущен. Попытка запуска..." -ForegroundColor Yellow
    
    try {
        Start-Process "redis-server" -WindowStyle Hidden
        Write-Host "✓ Redis запущен" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Невозможно запустить Redis. Celery может работать некорректно." -ForegroundColor Yellow
        Write-Host "Установите Redis с https://github.com/microsoftarchive/redis/releases" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ Redis уже запущен" -ForegroundColor Green
}

# Запуск Celery worker в фоновом режиме
Write-Host "`nЗапуск Celery worker..." -ForegroundColor Yellow
$celeryCmd = "celery -A myAfisha worker --loglevel=info"
Start-Process -FilePath "powershell" -ArgumentList "-Command", $celeryCmd -WindowStyle Normal

# Запуск Celery beat в фоновом режиме 
Write-Host "Запуск Celery beat..." -ForegroundColor Yellow
$beatCmd = "celery -A myAfisha beat --loglevel=info"
Start-Process -FilePath "powershell" -ArgumentList "-Command", $beatCmd -WindowStyle Normal

# Запуск Django сервера
Write-Host "`nЗапуск Django сервера..." -ForegroundColor Cyan
Write-Host "Для остановки сервера нажмите Ctrl+C`n" -ForegroundColor Yellow

python myAfisha/manage.py runserver

# Код для очистки (выполняется при завершении скрипта)
# Примечание: Этот блок может не выполниться, если процесс прерван через Ctrl+C
Write-Host "`n========================================" -ForegroundColor Yellow
Write-Host "  Завершение работы сервера" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

# Вывод информации о запущенных процессах
Write-Host "`nПримечание: Celery worker и beat могут все еще работать в фоновом режиме." -ForegroundColor Yellow
Write-Host "Для их остановки используйте Диспетчер задач Windows." -ForegroundColor Yellow 
