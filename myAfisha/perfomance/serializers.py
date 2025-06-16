from rest_framework import serializers
from .models import Performance, Review, PerformanceCategory, CartItem, PerformanceSchedule, Order, OrderItem

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(default=None)
    is_liked_by_current_user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'text', 'created_at', 'formatted_date', 
                 'likes_count', 'is_liked_by_current_user', 'can_edit']
        extra_kwargs = {'user': {'required': False, 'allow_null': True}}
    
    def get_likes_count(self, obj):
        """
        Возвращает количество лайков отзыва
        """
        return obj.likes.count()
    
    def get_is_liked_by_current_user(self, obj):
        """
        Проверяет, поставил ли текущий пользователь лайк этому отзыву
        Использует контекст для получения текущего пользователя
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_can_edit(self, obj):
        """
        Проверяет, может ли текущий пользователь редактировать отзыв
        Использует контекст для получения текущего пользователя
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            # Пользователь может редактировать свои отзывы или если он администратор
            return request.user == obj.user or request.user.is_staff
        return False
    
    def get_formatted_date(self, obj):
        """
        Возвращает отформатированную дату создания отзыва
        """
        return obj.created_at.strftime("%d.%m.%Y %H:%M")

class PerformanceSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', default=None)
    reviews = ReviewSerializer(many=True, read_only=True)
    upcoming_shows_count = serializers.SerializerMethodField()
    average_price = serializers.SerializerMethodField()
    is_popular = serializers.SerializerMethodField()
    duration_formatted = serializers.SerializerMethodField()
    nearest_show = serializers.SerializerMethodField()
    
    class Meta:
        model = Performance
        fields = ['id', 'name', 'description', 'image', 'category', 'duration_time', 
                 'duration_formatted', 'reviews', 'upcoming_shows_count', 
                 'average_price', 'is_popular', 'nearest_show']
    
    def get_upcoming_shows_count(self, obj):
        """
        Возвращает количество предстоящих показов спектакля
        """
        from django.utils import timezone
        return obj.schedule.filter(date_time__gt=timezone.now()).count()
    
    def get_average_price(self, obj):
        """
        Возвращает среднюю цену билета на спектакль
        """
        from django.db.models import Avg
        result = obj.schedule.aggregate(avg_price=Avg('price'))
        avg_price = result['avg_price']
        if avg_price:
            return f"{float(avg_price):.2f} ₽"
        return "Цена не указана"
    
    def get_is_popular(self, obj):
        """
        Определяет, является ли спектакль популярным
        """
        # Спектакль считается популярным, если на него есть более 3 отзывов
        # или более 5 предстоящих показов
        reviews_count = obj.reviews.count()
        from django.utils import timezone
        upcoming_shows = obj.schedule.filter(date_time__gt=timezone.now()).count()
        
        is_popular = reviews_count > 3 or upcoming_shows > 5
        return is_popular
    
    def get_duration_formatted(self, obj):
        """
        Возвращает продолжительность в удобном формате
        """
        if not obj.duration_time:
            return "Не указана"
        
        total_seconds = obj.duration_time.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        if hours > 0:
            return f"{hours} ч {minutes} мин"
        return f"{minutes} мин"
    
    def get_nearest_show(self, obj):
        """
        Возвращает информацию о ближайшем показе
        """
        from django.utils import timezone
        
        nearest = obj.schedule.filter(date_time__gt=timezone.now()).order_by('date_time').first()
        
        if nearest:
            return {
                'id': nearest.id,
                'date_time': nearest.date_time.strftime("%d.%m.%Y %H:%M"),
                'theater': nearest.theater.name if nearest.theater else "Не указан",
                'price': f"{float(nearest.price):.2f} ₽"
            }
        return None

class PerformanceBriefSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для спектакля с основной информацией для каталога
    """
    category = serializers.CharField(source='category.name', default=None)
    duration_formatted = serializers.SerializerMethodField()
    nearest_date = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Performance
        fields = ['id', 'name', 'image', 'category', 'duration_formatted', 'nearest_date', 'min_price']
    
    def get_duration_formatted(self, obj):
        """
        Возвращает продолжительность в удобном формате
        """
        if not obj.duration_time:
            return "Не указана"
        
        total_seconds = obj.duration_time.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        if hours > 0:
            return f"{hours} ч {minutes} мин"
        return f"{minutes} мин"
    
    def get_nearest_date(self, obj):
        """
        Возвращает ближайшую дату спектакля
        """
        from django.utils import timezone
        nearest = obj.schedule.filter(date_time__gt=timezone.now()).order_by('date_time').first()
        if nearest:
            return nearest.date_time.strftime("%d.%m.%Y %H:%M")
        return None
    
    def get_min_price(self, obj):
        """
        Возвращает минимальную цену билета
        """
        from django.db.models import Min
        result = obj.schedule.aggregate(min_price=Min('price'))
        min_price = result['min_price']
        if min_price:
            return f"{float(min_price):.2f} ₽"
        return "Не указана"

class CategoryWithPerformancesSerializer(serializers.ModelSerializer):
    """
    Сериализатор категории с вложенными спектаклями для отображения в каталоге
    """
    performances = PerformanceBriefSerializer(many=True, read_only=True, source='performances')
    performances_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PerformanceCategory
        fields = ['id', 'name', 'description', 'performances_count', 'performances']
    
    def get_performances_count(self, obj):
        """
        Возвращает количество спектаклей в категории
        """
        return obj.performances.count()

class CategoryBriefSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор категории для общего списка
    """
    performances_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PerformanceCategory
        fields = ['id', 'name', 'performances_count']
    
    def get_performances_count(self, obj):
        """
        Возвращает количество спектаклей в категории
        """
        return obj.performances.count()

class PerformanceScheduleSerializer(serializers.ModelSerializer):
    performance_name = serializers.CharField(source='performance.name', read_only=True)
    theater_name = serializers.CharField(source='theater.name', read_only=True)
    hall_number = serializers.CharField(source='hall.number_hall', read_only=True)
    
    class Meta:
        model = PerformanceSchedule
        fields = ['id', 'performance_name', 'theater_name', 'hall_number', 'date_time', 'available_seats', 'price']

class CartItemSerializer(serializers.ModelSerializer):
    performance_schedule = PerformanceScheduleSerializer(read_only=True)
    performance_schedule_id = serializers.PrimaryKeyRelatedField(
        queryset=PerformanceSchedule.objects.all(),
        write_only=True,
        source='performance_schedule'
    )
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'performance_schedule', 'performance_schedule_id', 'quantity', 'added_at', 'total_price']
        read_only_fields = ['added_at']

class OrderItemSerializer(serializers.ModelSerializer):
    performance_name = serializers.CharField(source='performance_schedule.performance.name', read_only=True)
    theater_name = serializers.CharField(source='performance_schedule.theater.name', read_only=True)
    date_time = serializers.DateTimeField(source='performance_schedule.date_time', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'performance_name', 'performance_schedule', 'theater_name', 
                 'date_time', 'quantity', 'price_per_unit', 'subtotal']
        read_only_fields = ['price_per_unit']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    formatted_created_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'status_display', 'total_amount', 
                 'created_at', 'formatted_created_date', 'updated_at',
                 'customer_name', 'customer_email', 'customer_phone', 
                 'payment_method', 'payment_id', 'items']
        read_only_fields = ['created_at', 'updated_at', 'total_amount']
    
    def get_formatted_created_date(self, obj):
        """
        Возвращает отформатированную дату создания заказа
        """
        return obj.created_at.strftime("%d.%m.%Y %H:%M")

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'customer_phone', 'payment_method', 'delivery_address']
    
    def validate_delivery_address(self, value):
        """
        Валидация формата адреса доставки.
        Адрес должен содержать улицу, номер дома, город и почтовый индекс.
        """
        # Если адрес не указан, пропускаем валидацию (адрес не обязателен)
        if not value:
            return value
            
        # Проверяем минимальную длину
        if len(value) < 10:
            raise serializers.ValidationError("Адрес доставки слишком короткий")
            
        # Проверяем наличие основных компонентов адреса
        required_parts = ['ул', 'д', 'г', 'индекс']
        missing_parts = []
        
        for part in required_parts:
            if part.lower() not in value.lower() and f'{part}.'.lower() not in value.lower():
                missing_parts.append(part)
                
        if missing_parts:
            raise serializers.ValidationError(
                f"Адрес должен содержать: {', '.join(missing_parts)}. "
                f"Формат: ул. Название, д. Номер, г. Город, индекс Индекс"
            )
            
        # Проверяем наличие почтового индекса в формате 6 цифр
        import re
        if not re.search(r'\b\d{6}\b', value):
            raise serializers.ValidationError(
                "Адрес должен содержать почтовый индекс в формате 6 цифр"
            )
            
        return value
    
    def validate(self, attrs):
        """
        Валидация заказа: проверка минимальной и максимальной суммы заказа.
        """
        # Получаем пользователя из контекста
        user = self.context['request'].user
        
        # Получаем элементы корзины пользователя
        from .models import CartItem
        cart_items = CartItem.objects.filter(user=user)
        
        # Проверяем наличие элементов в корзине
        if not cart_items.exists():
            raise serializers.ValidationError({
                "non_field_errors": ["Корзина пуста"]
            })
        
        # Проверяем доступность мест для каждого элемента корзины
        for cart_item in cart_items:
            if cart_item.quantity > cart_item.performance_schedule.available_seats:
                raise serializers.ValidationError({
                    "non_field_errors": [
                        f"Недостаточно мест для '{cart_item.performance_schedule.performance.name}'. "
                        f"Доступно: {cart_item.performance_schedule.available_seats}, "
                        f"запрошено: {cart_item.quantity}"
                    ]
                })
        
        # Рассчитываем общую сумму заказа
        total_amount = sum(item.performance_schedule.price * item.quantity for item in cart_items)
        
        # Проверка минимальной суммы заказа (500 рублей)
        if total_amount < 500:
            raise serializers.ValidationError({
                "non_field_errors": [
                    f"Минимальная сумма заказа 500 руб. Текущая сумма: {total_amount} руб."
                ]
            })
            
        # Проверка максимальной суммы заказа (100 000 рублей)
        if total_amount > 100000:
            raise serializers.ValidationError({
                "non_field_errors": [
                    f"Максимальная сумма заказа 100 000 руб. Текущая сумма: {total_amount} руб."
                ]
            })
            
        return attrs
        
    def create(self, validated_data):
        # Получаем пользователя из контекста
        user = self.context['request'].user
        
        # Получаем элементы корзины пользователя
        from .models import CartItem
        cart_items = CartItem.objects.filter(user=user)
        
        # Рассчитываем общую сумму заказа
        total_amount = sum(item.performance_schedule.price * item.quantity for item in cart_items)
        
        # Создаем заказ
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            **validated_data
        )
        
        try:
            # Создаем элементы заказа на основе элементов корзины
            for cart_item in cart_items:
                # Резервируем места
                if not cart_item.performance_schedule.reserve_seats(cart_item.quantity):
                    # Если не удалось зарезервировать места, отменяем заказ
                    raise serializers.ValidationError(
                        f"Недостаточно мест для '{cart_item.performance_schedule.performance.name}'. "
                        f"Доступно: {cart_item.performance_schedule.available_seats}"
                    )
                
                # Создаем элемент заказа
                OrderItem.objects.create(
                    order=order,
                    performance_schedule=cart_item.performance_schedule,
                    quantity=cart_item.quantity,
                    price_per_unit=cart_item.performance_schedule.price
                )
            
            # Очищаем корзину пользователя только если все места успешно зарезервированы
            cart_items.delete()
            
            return order
            
        except Exception as e:
            # В случае ошибки отменяем заказ и пробрасываем исключение
            order.delete()
            raise serializers.ValidationError(str(e))