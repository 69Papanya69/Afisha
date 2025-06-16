from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Order
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_reminder_emails():
    """
    Отправляет напоминания о новых спектаклях пользователям
    """
    try:
        # Получаем пользователей, которые сделали заказ за последние 3 месяца
        three_months_ago = timezone.now() - timedelta(days=90)
        active_users = User.objects.filter(orders__created_at__gte=three_months_ago).distinct()
        
        sent_count = 0
        for user in active_users:
            # В реальном приложении здесь должна быть логика отправки персонализированных рекомендаций
            # На основе интересов пользователя, истории просмотров, покупок и т.д.
            subject = "Новые спектакли в нашей афише!"
            message = f"Здравствуйте, {user.username}! Приходите посмотреть новые спектакли в нашем театре!"
            
            # В реальном приложении здесь будет реальная отправка email
            # send_mail(
            #     subject,
            #     message,
            #     settings.DEFAULT_FROM_EMAIL,
            #     [user.email],
            #     fail_silently=False,
            # )
            
            # Для тестирования выводим сообщение в лог
            logger.info(f"[EMAIL] To: {user.email}, Subject: {subject}")
            sent_count += 1
            
        return f"Отправлено {sent_count} напоминаний"
        
    except Exception as e:
        logger.error(f"Ошибка при отправке напоминаний: {str(e)}")
        raise 