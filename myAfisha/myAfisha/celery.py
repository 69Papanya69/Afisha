import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myAfisha.settings')

app = Celery('myAfisha')

# Использовать настройки из Django settings с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находить и регистрировать задачи из всех приложений Django
app.autodiscover_tasks()

# Настройка периодических задач
app.conf.beat_schedule = {
    'check-expired-performances': {
        'task': 'perfomance.tasks.check_expired_performances',
        'schedule': crontab(hour=0, minute=0),  # Выполнять каждый день в полночь
    },
    'update-performance-stats': {
        'task': 'perfomance.tasks.update_performance_stats',
        'schedule': crontab(minute='*/30'),  # Выполнять каждые 30 минут
    },
    'send-reminder-emails': {
        'task': 'users.tasks.send_reminder_emails',
        'schedule': crontab(hour=10, minute=0, day_of_week='mon,wed,fri'),  # Понедельник, среда, пятница в 10:00
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 