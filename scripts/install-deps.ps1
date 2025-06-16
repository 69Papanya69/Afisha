#!/usr/bin/env pwsh
# Скрипт для установки всех необходимых зависимостей для разработки

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Установка зависимостей для myAfisha" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка наличия Python
try {
    $pythonVersion = python --version
    Write-Host "✓ Python установлен: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python не установлен или не добавлен в PATH!" -ForegroundColor Red
    Write-Host "Установите Python с https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Проверка наличия pip
try {
    $pipVersion = pip --version
    Write-Host "✓ pip установлен: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ pip не установлен!" -ForegroundColor Red
    Write-Host "Обновите Python или установите pip отдельно" -ForegroundColor Yellow
    exit 1
}

# Проверка наличия Docker
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker установлен: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ Docker не установлен или не запущен!" -ForegroundColor Yellow
    Write-Host "Для работы с Docker установите Docker Desktop с https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    $installDocker = Read-Host "Продолжить без Docker? (y/n)"
    if ($installDocker -ne "y") {
        exit 1
    }
}

# Настройка виртуальной среды
$venvPath = ".venv"
$activateScript = "$venvPath\Scripts\Activate.ps1"

Write-Host "`nШаг 1: Настройка виртуальной среды Python..." -ForegroundColor Cyan

if (-not (Test-Path $venvPath)) {
    Write-Host "Создание виртуальной среды в $venvPath..." -ForegroundColor Yellow
    python -m venv $venvPath
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Ошибка создания виртуальной среды!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Виртуальная среда создана" -ForegroundColor Green
} else {
    Write-Host "✓ Виртуальная среда уже существует" -ForegroundColor Green
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
Write-Host "✓ Виртуальная среда активирована" -ForegroundColor Green

# Обновление pip
Write-Host "`nОбновление pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Установка зависимостей из requirements.txt
if (Test-Path "requirements.txt") {
    Write-Host "`nШаг 2: Установка зависимостей из requirements.txt..." -ForegroundColor Cyan
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Ошибка установки зависимостей!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Зависимости установлены" -ForegroundColor Green
} else {
    Write-Host "⚠ Файл requirements.txt не найден!" -ForegroundColor Yellow
}

# Установка дополнительных зависимостей для разработки
Write-Host "`nШаг 3: Установка зависимостей для разработки..." -ForegroundColor Cyan
$devDeps = @(
    "black",         # Форматирование кода
    "flake8",        # Линтер
    "pytest",        # Тестирование
    "pytest-django", # Тестирование Django
    "ipython",       # Улучшенная Python консоль
    "django-debug-toolbar" # Инструменты отладки для Django
)

foreach ($dep in $devDeps) {
    Write-Host "Установка $dep..." -ForegroundColor Yellow
    pip install $dep
}
Write-Host "✓ Зависимости для разработки установлены" -ForegroundColor Green

# Проверка Redis для локальной разработки
Write-Host "`nШаг 4: Проверка Redis..." -ForegroundColor Cyan
$redisInstalled = $false

try {
    $redisService = Get-Service -Name "Redis" -ErrorAction SilentlyContinue
    if ($redisService) {
        $redisInstalled = $true
        Write-Host "✓ Redis установлен как служба Windows" -ForegroundColor Green
    } else {
        $redisExe = Get-Command "redis-server" -ErrorAction SilentlyContinue
        if ($redisExe) {
            $redisInstalled = $true
            Write-Host "✓ Redis установлен как исполняемый файл" -ForegroundColor Green
        }
    }
} catch {
    # Ничего не делаем, просто продолжаем
}

if (-not $redisInstalled) {
    Write-Host "⚠ Redis не установлен!" -ForegroundColor Yellow
    Write-Host "Для работы Celery локально рекомендуется установить Redis:" -ForegroundColor Yellow
    Write-Host "- Для Windows: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Yellow
    Write-Host "- Альтернативно, используйте Docker для запуска Redis" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Установка зависимостей завершена!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Для запуска проекта выполните один из следующих скриптов:" -ForegroundColor Yellow
Write-Host "- С Docker:    ./scripts/docker-deploy.ps1" -ForegroundColor White
Write-Host "- Без Docker:  ./scripts/start-dev.ps1" -ForegroundColor White
Write-Host "" 
