from django.db import models
from typing import Any  # str не нужно импортировать, это встроенный тип

# Create your models here.
# main/models.py
class Theater(models.Model):
    """
    Модель театра.
    
    Представляет театр с названием, адресом и описанием.
    """
    name = models.CharField(max_length=255, verbose_name='Название театра')
    address = models.TextField(verbose_name='Адресс')
    description = models.TextField(verbose_name='Подробности')
    
    class Meta:
        ordering = ['name']  # Сортировка по названию театра
        verbose_name="Театр"
        verbose_name_plural = "Театры"
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта театра.
        
        Returns:
            str: Название театра
        """
        return self.name

class Hall(models.Model):
    """
    Модель зала театра.
    
    Представляет зал с номером, принадлежащий конкретному театру.
    """
    number_hall = models.IntegerField(verbose_name="Номер зала")
    theater = models.ForeignKey(
        Theater, 
        on_delete=models.CASCADE, 
        related_name='halls',
        verbose_name="Театр", 
        null=True
    )
    
    class Meta:
        verbose_name="Зал"
        verbose_name_plural = "Залы"
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта зала.
        
        Returns:
            str: Номер зала
        """
        return f"{self.number_hall}"

    
    
    
    