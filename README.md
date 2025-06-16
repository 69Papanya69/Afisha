# myAfisha с Celery и Docker

Проект афиши мероприятий с периодическими задачами через Celery в Docker.

## Функциональность

- Основной сайт афиш на Django
- Периодические задачи через Celery:
  - Проверка истекших спектаклей (каждый день в полночь)
  - Обновление статистики спектаклей (каждые 30 минут)
  - Отправка напоминаний пользователям (понедельник, среда, пятница в 10:00)
- Мониторинг Celery через Flower

## Запуск проекта в Docker

Убедитесь, что у вас установлены Docker и Docker Compose.

```bash
# Сборка контейнеров
docker-compose build

# Запуск всех сервисов
docker-compose up -d

# Применение миграций
docker-compose exec web python myAfisha/manage.py migrate

# Создание суперпользователя
docker-compose exec web python myAfisha/manage.py createsuperuser
```

После запуска сервисов будут доступны:
- Django: http://localhost:8000/
- Django Admin: http://localhost:8000/admin/
- Flower (мониторинг Celery): http://localhost:5555/
- Django Silk (профилирование): http://localhost:8000/silk/

## Использование Makefile

Для удобства работы с проектом можно использовать команды из Makefile:

```bash
# Сборка и запуск
make build
make up

# Миграции и создание суперпользователя
make migrate
make createsuperuser

# Просмотр логов
make logs

# Остановка контейнеров
make down
```

## Запуск на Windows (без Docker)

Для локального запуска Celery на Windows можно использовать скрипт `celery_start.bat`.
Предварительно нужно установить все зависимости:

```bash
pip install -r requirements.txt
pip install eventlet  # для работы Celery на Windows
```

После установки запустите скрипт `celery_start.bat`. 