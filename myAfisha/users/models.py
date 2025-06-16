from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
import re
from django.core import validators

def validate_address_format(value):
    """
    Validates that the address format is correct.
    Format should be: город, улица, дом, квартира (optional)
    """
    # Simple validation to ensure address has at least city and street
    if len(value.split(',')) < 2:
        raise ValidationError(
            'Адрес должен содержать минимум город и улицу, разделенные запятой'
        )
    return value

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name='Картинка профиля')

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    def get_profile_image_url(self):
        """ Возвращает корректный URL к изображению профиля """
        if self.profile_image:
            return f"{settings.MEDIA_URL}{self.profile_image}"
        return f"{settings.MEDIA_URL}profile_images/default_profile_image.png"