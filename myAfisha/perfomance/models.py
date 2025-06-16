from django.db import models
from django.utils import timezone
from django.urls import reverse
from main.models import Hall, Theater
from users.models import User

# Категория спектакля
class PerformanceCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Имя')
    description = models.TextField(blank=True, null=True, verbose_name='Подробности')

    class Meta:
        verbose_name = 'Категория спектакля'
        verbose_name_plural = "Категории спектаклей"

    def __str__(self):
        return self.name


# Спектакль (без театра и зала)
class Performance(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя')
    description = models.TextField(verbose_name='Подробности')
    duration_time = models.DurationField(verbose_name='Время продолжительности')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    image = models.ImageField(upload_to='performances/', blank=True, null=True, verbose_name='Изображение')
    file = models.FileField(upload_to='performance_files/', blank=True, null=True, verbose_name='Файл')
    category = models.ForeignKey(
        PerformanceCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='performances',
        verbose_name='Категория спектакля'
    )
    related_link = models.URLField(max_length=200, blank=True, null=True, verbose_name='Ссылка на дополнительную информацию')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Спектакль'
        verbose_name_plural = "Спектакли"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('performance_detail', args=[self.id])


# Расписание спектакля
class PerformanceSchedule(models.Model):
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE, related_name='schedule', verbose_name='Спектакль')
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='schedule', verbose_name='Театр',  null=True)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='schedule', verbose_name='Зал', null=True)
    date_time = models.DateTimeField(verbose_name='Дата и время')
    available_seats = models.IntegerField(verbose_name='Количество мест')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена билета')

    class Meta:
        verbose_name = 'Расписание спектаклей'
        verbose_name_plural = "Расписание спектаклей"

    def __str__(self):
        return f"{self.performance.name} - {self.date_time}"

    def reserve_seats(self, quantity):
        """
        Бронирует указанное количество мест для данного расписания.
        Возвращает True, если бронирование успешно, False если недостаточно мест.
        """
        if self.available_seats >= quantity:
            self.available_seats -= quantity
            self.save()
            return True
        return False

    def release_seats(self, quantity):
        """
        Освобождает указанное количество мест для данного расписания.
        """
        self.available_seats += quantity
        self.save()


# Акции
class Promotion(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Подробности')
    discount_percentage = models.FloatField(verbose_name='Процент скидки')
    start_date = models.DateTimeField(verbose_name='Дата старта акции')
    end_date = models.DateTimeField(verbose_name='Дата окончания акции')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания акции')
    performances = models.ManyToManyField(Performance, related_name='promotions', verbose_name='Спектакль')

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = "Акции"

    def __str__(self):
        return self.title


# Отзыв
class Review(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews', verbose_name='Пользователь', null=True, blank=True)
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE, related_name='reviews', verbose_name='Спектакль')
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.performance.name}"


# Лайк
class Like(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='likes', verbose_name='Пользователь')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes', verbose_name='Отзыв')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = "Лайки"


# Заглушка
class PlaceholderRelation(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    # Добавляем связь ManyToMany с Performance через промежуточную модель PlaceholderThrough
    related_performances = models.ManyToManyField(
        'Performance',
        through='PlaceholderThrough',
        related_name='placeholder_relations',
        verbose_name='Связанные спектакли (через заглушку)'
    )

    class Meta:
        verbose_name = 'Заглушка'
        verbose_name_plural = 'Заглушки'

    def __str__(self):
        return self.name


class PlaceholderThrough(models.Model):
    placeholder = models.ForeignKey('PlaceholderRelation', on_delete=models.CASCADE, verbose_name='Заглушка')
    related_object = models.ForeignKey('Performance', on_delete=models.CASCADE, verbose_name='Связанный объект')
    added_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Связь заглушки'
        verbose_name_plural = 'Связи заглушек'


# Корзина для спектаклей
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', verbose_name='Пользователь')
    performance_schedule = models.ForeignKey(PerformanceSchedule, on_delete=models.CASCADE, related_name='cart_items', verbose_name='Расписание спектакля')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество билетов')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        unique_together = ('user', 'performance_schedule')

    def __str__(self):
        return f"{self.user.username} - {self.performance_schedule.performance.name} ({self.quantity})"
    
    @property
    def total_price(self):
        """
        Возвращает общую стоимость элемента корзины
        """
        return self.performance_schedule.price * self.quantity


# Статусы заказа
class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'В обработке'
    CONFIRMED = 'confirmed', 'Подтвержден'
    CANCELLED = 'cancelled', 'Отменен'
    COMPLETED = 'completed', 'Выполнен'


# Заказ
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name='Статус'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая сумма')
    customer_name = models.CharField(max_length=255, verbose_name='Имя заказчика')
    customer_email = models.EmailField(verbose_name='Email заказчика')
    customer_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон заказчика')
    payment_method = models.CharField(max_length=50, default='Онлайн', verbose_name='Метод оплаты')
    payment_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='Идентификатор платежа')
    delivery_address = models.TextField(blank=True, null=True, verbose_name='Адрес доставки')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ #{self.id} ({self.user.username})"
    
    def calculate_total(self):
        """
        Рассчитывает общую сумму заказа на основе элементов заказа
        """
        return sum(item.subtotal for item in self.items.all())

    def cancel(self):
        """
        Отменяет заказ и возвращает количество мест в расписание
        """
        if self.status != OrderStatus.CANCELLED:
            # Возвращаем места в расписание
            for item in self.items.all():
                item.performance_schedule.release_seats(item.quantity)
            
            self.status = OrderStatus.CANCELLED
            self.save()
            return True
        return False


# Элемент заказа
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    performance_schedule = models.ForeignKey(PerformanceSchedule, on_delete=models.PROTECT, verbose_name='Расписание спектакля')
    quantity = models.PositiveIntegerField(verbose_name='Количество билетов')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за билет')
    
    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
    
    def __str__(self):
        return f"{self.performance_schedule.performance.name} x{self.quantity} ({self.order})"
    
    @property
    def subtotal(self):
        """
        Возвращает общую стоимость элемента заказа
        """
        return self.price_per_unit * self.quantity