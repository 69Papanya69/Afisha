@echo off
echo Запуск Celery Worker и Beat для проекта myAfisha...

REM Запуск Celery Worker
start cmd /k "cd myAfisha && celery -A myAfisha worker --loglevel=info -P eventlet"

REM Запуск Celery Beat
start cmd /k "cd myAfisha && celery -A myAfisha beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"

echo Celery Worker и Beat запущены! 