# Скрипты для проекта myAfisha

Этот каталог содержит набор PowerShell скриптов для автоматизации различных задач при разработке и развертывании проекта myAfisha.

## Требования

* Windows 10 или выше
* PowerShell 5.1 или выше
* Python 3.8+ (для локальной разработки)
* Docker Desktop (для контейнеризации)

## Разрешение на выполнение скриптов

Перед использованием скриптов может потребоваться разрешить их выполнение в PowerShell. Выполните в PowerShell с правами администратора:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Доступные скрипты

### Установка и настройка

* **install-deps.ps1** - Установка всех необходимых зависимостей для разработки
  ```powershell
  .\scripts\install-deps.ps1
  ```

### Работа с Docker

* **docker-deploy.ps1** - Полное развертывание проекта в Docker (сборка, запуск, миграции)
  ```powershell
  .\scripts\docker-deploy.ps1
  ```

* **docker-stop.ps1** - Остановка и удаление контейнеров
  ```powershell
  .\scripts\docker-stop.ps1            # Остановка контейнеров (сохраняя тома данных)
  .\scripts\docker-stop.ps1 -removeVolumes  # Остановка и полное удаление с томами данных
  ```

* **docker-logs.ps1** - Просмотр логов контейнеров
  ```powershell
  .\scripts\docker-logs.ps1                  # Просмотр логов всех сервисов
  .\scripts\docker-logs.ps1 -service web     # Просмотр логов только веб-сервиса
  .\scripts\docker-logs.ps1 -service celery_worker -lines 200  # Просмотр 200 последних строк логов
  .\scripts\docker-logs.ps1 -follow $false   # Показать логи без режима следования (выход после вывода)
  ```

* **docker-admin.ps1** - Выполнение административных команд Django в контейнере
  ```powershell
  .\scripts\docker-admin.ps1 help            # Показать справку по доступным командам
  .\scripts\docker-admin.ps1 createsuperuser # Создать суперпользователя
  .\scripts\docker-admin.ps1 makemigrations  # Создать миграции
  .\scripts\docker-admin.ps1 migrate         # Применить миграции
  .\scripts\docker-admin.ps1 shell           # Запустить интерактивную оболочку Django
  .\scripts\docker-admin.ps1 test            # Запустить тесты
  ```

### Локальная разработка (без Docker)

* **start-dev.ps1** - Запуск проекта в режиме разработки
  ```powershell
  .\scripts\start-dev.ps1                     # Запуск с миграцией и сбором статики
  .\scripts\start-dev.ps1 -noMigrations       # Запуск без применения миграций  
  .\scripts\start-dev.ps1 -noStatic           # Запуск без сбора статических файлов
  ```

## Порты и доступ

При запуске Docker будут доступны следующие сервисы:

* Django: http://localhost:8000/
* Django Admin: http://localhost:8000/admin/
* Django Silk: http://localhost:8000/silk/
* Flower (мониторинг Celery): http://localhost:5555/ 
