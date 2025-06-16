# Импорт celery app должен выполниться при загрузке Django
from .celery import app as celery_app

__all__ = ('celery_app',)



