from celery import shared_task
from django.utils import timezone
from .models import PerformanceSchedule, Performance
from django.db.models import Count, Sum, Avg
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_expired_performances():
    """
    Проверяет и помечает истекшие показы спектаклей
    """
    now = timezone.now()
    expired_schedules = PerformanceSchedule.objects.filter(date_time__lt=now)
    expired_count = expired_schedules.update(available_seats=0)
    
    logger.info(f"Помечено {expired_count} истекших показов спектаклей")
    return f"Обработано {expired_count} истекших показов"

@shared_task
def update_performance_stats():
    """
    Обновляет статистику просмотров спектаклей
    """
    try:
        # Подсчитываем статистику для всех спектаклей
        performances = Performance.objects.all()
        total_count = performances.count()
        
        # Здесь можно имплементировать реальное обновление статистики,
        # например, подсчет количества просмотров, лайков, отзывов и т.д.
        
        # Пример агрегирования данных
        top_performances = Performance.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating', default=0)
        ).order_by('-avg_rating')[:5]
        
        for perf in top_performances:
            logger.info(f"Спектакль '{perf.name}': {perf.review_count} отзывов, рейтинг {perf.avg_rating}")
            
        return f"Обновлена статистика для {total_count} спектаклей"
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении статистики: {str(e)}")
        raise 