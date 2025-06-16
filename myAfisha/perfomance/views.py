# views.py
from django.http import JsonResponse, HttpRequest
from django.db import IntegrityError
from main.models import Hall
from .models import Performance, PerformanceCategory, Promotion, Review, CartItem, PerformanceSchedule, Order, OrderStatus
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PerformanceSerializer
from django.db.models import Count, Avg, Sum
from rest_framework.generics import RetrieveAPIView, ListAPIView, ListCreateAPIView
from .promotion_serializers import PromotionSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import Review
from .serializers import ReviewSerializer
from .models import CartItem, PerformanceSchedule
from .serializers import CartItemSerializer
from django.db import IntegrityError
from django.db.models import F, Q, Min, Max
from .serializers import PerformanceScheduleSerializer, CartItemSerializer, ReviewSerializer, OrderSerializer, OrderCreateSerializer, PerformanceBriefSerializer, CategoryWithPerformancesSerializer, CategoryBriefSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import PerformanceFilter
from typing import List, Dict, Any, Union, Optional
from django.utils import timezone

def get_halls_by_theater(request: HttpRequest) -> JsonResponse:
    """
    Получает список залов для указанного театра.
    
    Args:
        request (HttpRequest): HTTP запрос с параметром theater_id
        
    Returns:
        JsonResponse: JSON с идентификаторами и номерами залов
        
    Example:
        GET /api/halls/?theater_id=1
    """
    theater_id = request.GET.get('theater_id')
    if not theater_id:
        return JsonResponse([], safe=False)

    halls = Hall.objects.filter(theater_id=theater_id).values('id', 'number_hall')
    return JsonResponse(list(halls), safe=False)

def get_performances(request: HttpRequest) -> JsonResponse:
    """
    Получает список всех спектаклей с основной информацией.
    
    Args:
        request (HttpRequest): HTTP запрос
        
    Returns:
        JsonResponse: JSON со списком спектаклей (id, name, image)
    """
    performances = Performance.objects.all().values('id', 'name', 'image')
    return JsonResponse(list(performances), safe=False)

def performances_by_category(request: HttpRequest, category_name: str) -> JsonResponse:
    """
    Получает список спектаклей определенной категории по названию категории.
    
    Args:
        request (HttpRequest): HTTP запрос
        category_name (str): Название категории спектаклей
        
    Returns:
        JsonResponse: JSON со списком спектаклей данной категории
    """
    # Вариант 1: метод filter с двойным подчеркиванием для поиска по связанной таблице
    performances = Performance.objects.filter(category__name=category_name)
    data = list(performances.values('id', 'name', 'description'))
    return JsonResponse(data, safe=False)

def performances_by_category_related(request: HttpRequest, category_id: int) -> JsonResponse:
    """
    Получает список спектаклей определенной категории по ID категории,
    используя связь через related_name.
    
    Args:
        request (HttpRequest): HTTP запрос
        category_id (int): ID категории спектаклей
        
    Returns:
        JsonResponse: JSON со списком спектаклей данной категории или сообщение об ошибке
        
    Raises:
        PerformanceCategory.DoesNotExist: Если категория с указанным ID не найдена
    """
    # Вариант 2: обращение к связанной таблице через related_name
    try:
        category = PerformanceCategory.objects.get(id=category_id)
        performances = category.performances.all()
        data = list(performances.values('id', 'name', 'description'))
        return JsonResponse(data, safe=False)
    except PerformanceCategory.DoesNotExist:
        return JsonResponse({'error': 'Категория не найдена'}, status=404)

def performances_exclude_category(request: HttpRequest, category_name: str) -> JsonResponse:
    """
    Получает список спектаклей, не относящихся к указанной категории.
    
    Args:
        request (HttpRequest): HTTP запрос
        category_name (str): Название категории для исключения
        
    Returns:
        JsonResponse: JSON со списком спектаклей, не относящихся к указанной категории
    """
    # Пример использования exclude(): получить все спектакли, НЕ относящиеся к категории с указанным именем
    performances = Performance.objects.exclude(category__name=category_name)
    data = list(performances.values('id', 'name', 'description'))
    return JsonResponse(data, safe=False)

def performances_ordered_by_name(request):
    """
    Пример использования order_by(): получить все спектакли, отсортированные по имени (в алфавитном порядке)
    """
    performances = Performance.objects.all().order_by('name')
    data = list(performances.values('id', 'name', 'description'))
    return JsonResponse(data, safe=False)

def performances_ordered_by_created_desc(request):
    """
    Пример использования order_by(): получить все спектакли, отсортированные по дате создания (сначала новые)
    """
    performances = Performance.objects.all().order_by('-created_at')
    data = list(performances.values('id', 'name', 'description', 'created_at'))
    return JsonResponse(data, safe=False)

def category_performance_count(request):
    """
    Агрегирование: получить количество спектаклей в каждой категории
    """
    categories = PerformanceCategory.objects.annotate(perf_count=Count('performances'))
    data = list(categories.values('id', 'name', 'perf_count'))
    return JsonResponse(data, safe=False)

def average_performance_duration(request):
    """
    Агрегирование: получить среднюю продолжительность спектакля
    """
    avg_duration = Performance.objects.aggregate(avg_duration=Avg('duration_time'))
    return JsonResponse(avg_duration)

def total_seats_in_theater(request, theater_id):
    """
    Агрегирование: получить суммарное количество мест во всех залах театра
    """
    from main.models import Hall
    total_seats = Hall.objects.filter(theater_id=theater_id).aggregate(total=Sum('available_seats'))
    return JsonResponse(total_seats)

def get_performance_values(request):
    """
    Пример использования values(): получение данных о спектаклях с указанием полей
    """
    data = list(Performance.objects.values('name', 'category__name', 'created_at'))
    return JsonResponse(data, safe=False)

def get_performance_values_list(request):
    """
    Пример использования values_list(): получение данных о спектаклях в виде списка кортежей
    """
    data = list(Performance.objects.values_list('name', 'category__name', 'created_at'))
    return JsonResponse(data, safe=False)

class PerformanceListView(APIView):
    def get(self, request):
        performances = Performance.objects.select_related('category').prefetch_related('reviews', 'schedule').all()
        
        # Используем сериализатор с контекстом запроса
        serializer = PerformanceSerializer(
            performances, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)

class FilteredPerformanceListView(ListAPIView):
    """
    Представление для списка спектаклей с фильтрацией
    
    Доступные фильтры:
    - name: Фильтр по названию (поиск по частичному совпадению)
    - category: Фильтр по ID категории
    - category_name: Фильтр по названию категории
    - min_price: Минимальная цена билета
    - max_price: Максимальная цена билета
    - date_after: Спектакли после указанной даты (формат YYYY-MM-DD)
    - date_before: Спектакли до указанной даты (формат YYYY-MM-DD)
    - min_seats: Минимальное количество доступных мест
    - min_duration: Минимальная продолжительность в минутах
    - max_duration: Максимальная продолжительность в минутах
    - theater: Фильтр по названию театра
    
    Доступна сортировка по полям:
    - name: Название спектакля
    - created_at: Дата создания
    
    Доступен поиск по полям:
    - name: Название спектакля
    - description: Описание спектакля
    """
    queryset = Performance.objects.select_related('category').prefetch_related('reviews', 'schedule').all()
    serializer_class = PerformanceSerializer
    filterset_class = PerformanceFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

class PerformanceDetailView(RetrieveAPIView):
    queryset = Performance.objects.select_related('category').prefetch_related('reviews', 'schedule').all()
    serializer_class = PerformanceSerializer
    
    def get_serializer_context(self):
        """
        Добавляем запрос в контекст сериализатора
        """
        context = super().get_serializer_context()
        return context

class PerformanceWithReviewsView(APIView):
    def get(self, request):
        performances = Performance.objects.prefetch_related('reviews').all()
        data = [
            {
                'id': performance.id,
                'name': performance.name,
                'reviews': [
                    {
                        'user': review.user.username,
                        'text': review.text,
                        'created_at': review.created_at
                    }
                    for review in performance.reviews.all()
                ]
            }
            for performance in performances
        ]
        return Response(data)

class PromotionListView(ListAPIView):
    serializer_class = PromotionSerializer

    def get_queryset(self):
        return Promotion.objects.order_by('-start_date')[:3]

class LastPerformanceListView(ListAPIView):
    serializer_class = PerformanceSerializer

    def get_queryset(self):
        return Performance.objects.order_by('-created_at')[:3]

def update_performances_category(request):
    """
    Массовое обновление: пример использования update().
    Меняет категорию всех спектаклей с name='Старая категория' на категорию с id=1.
    Обычно используется для быстрого изменения сразу у многих записей.
    """
    updated_count = Performance.objects.filter(category__name='Старая категория').update(category_id=1)
    return JsonResponse({'updated': updated_count})


def delete_performances_by_category(request):
    """
    Массовое удаление: пример использования delete().
    Удаляет все спектакли с категорией 'Удалить'.
    Обычно используется для быстрого удаления сразу у многих записей.
    """
    deleted_count, _ = Performance.objects.filter(category__name='Удалить').delete()
    return JsonResponse({'deleted': deleted_count})

@api_view(['GET'])
def search_performances(request):
    query = request.GET.get('q', '')
    performances = Performance.objects.filter(name__icontains=query)
    
    # Передаем контекст запроса в сериализатор
    serializer = PerformanceSerializer(
        performances, 
        many=True, 
        context={'request': request}
    )
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, pk):
    try:
        performance = Performance.objects.get(pk=pk)
    except Performance.DoesNotExist:
        return Response({'error': 'Спектакль не найден.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Передаем контекст с запросом в сериализатор
    serializer = ReviewSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        # Если пользователь авторизован, сохраняем его, иначе user=None
        user = request.user if request.user.is_authenticated else None
        serializer.save(user=user, performance=performance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_review(request, pk):
    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        return Response({'error': 'Отзыв не найден.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Проверяем права на редактирование
    if review.user != request.user and not request.user.is_staff:
        return Response({'error': 'Можно редактировать только свои отзывы.'}, status=status.HTTP_403_FORBIDDEN)
    
    # Передаем контекст с запросом в сериализатор
    serializer = ReviewSerializer(review, data=request.data, partial=True, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        return Response({'error': 'Отзыв не найден.'}, status=status.HTTP_404_NOT_FOUND)
    if review.user != request.user:
        return Response({'error': 'Можно удалять только свои отзывы.'}, status=status.HTTP_403_FORBIDDEN)
    review.delete()
    return Response({'success': 'Отзыв удалён.'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_review(request, pk):
    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        return Response({'error': 'Отзыв не найден.'}, status=status.HTTP_404_NOT_FOUND)
    user = request.user
    if not (user.is_staff or user.is_superuser):
        return Response({'error': 'Только администратор может удалять чужие отзывы.'}, status=status.HTTP_403_FORBIDDEN)
    review.delete()
    return Response({'success': 'Отзыв удалён администратором.'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_performance(request, pk):
    try:
        performance = Performance.objects.get(pk=pk)
    except Performance.DoesNotExist:
        return Response({'error': 'Спектакль не найден.'}, status=status.HTTP_404_NOT_FOUND)
    user = request.user
    if not (user.is_staff or user.is_superuser):
        return Response({'error': 'Только администратор может удалять спектакли.'}, status=status.HTTP_403_FORBIDDEN)
    performance.delete()
    return Response({'success': 'Спектакль удалён администратором.'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_list(request):
    """
    Получение списка всех элементов в корзине текущего пользователя
    """
    cart_items = CartItem.objects.filter(user=request.user)
    serializer = CartItemSerializer(cart_items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cart_add(request):
    """
    Добавление билетов в корзину
    """
    try:
        data = request.data
        performance_schedule_id = data.get('performance_schedule_id')
        quantity = int(data.get('quantity', 1))
        
        # Проверяем наличие обязательных полей
        if not performance_schedule_id:
            return Response({"error": "Не указан ID расписания спектакля"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Проверяем корректность значения quantity
        if quantity <= 0:
            return Response({"error": "Количество должно быть положительным числом"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем расписание спектакля
        try:
            performance_schedule = PerformanceSchedule.objects.get(pk=performance_schedule_id)
        except PerformanceSchedule.DoesNotExist:
            return Response({"error": "Расписание спектакля не найдено"}, status=status.HTTP_404_NOT_FOUND)
        
        # Проверяем наличие достаточного количества мест
        if performance_schedule.available_seats < quantity:
            return Response({
                "error": f"Недостаточно мест. Доступно: {performance_schedule.available_seats}, запрошено: {quantity}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        # Проверяем, есть ли уже этот спектакль в корзине пользователя
        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            performance_schedule=performance_schedule,
            defaults={'quantity': quantity}
        )
        
        # Если элемент уже был в корзине, обновляем количество
        if not created:
            # Проверяем наличие достаточного количества мест с учетом уже имеющегося количества в корзине
            if performance_schedule.available_seats < (quantity - cart_item.quantity):
                return Response({
                    "error": f"Недостаточно мест. Доступно: {performance_schedule.available_seats}, "
                             f"уже в корзине: {cart_item.quantity}, запрошено дополнительно: {quantity - cart_item.quantity}"
                }, status=status.HTTP_400_BAD_REQUEST)
                
            cart_item.quantity = quantity
            cart_item.save()
        
        # Сериализуем элемент корзины для ответа
        serializer = CartItemSerializer(cart_item)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cart_update_quantity(request, item_id):
    """
    Обновление количества билетов в корзине
    """
    try:
        # Получаем элемент корзины
        try:
            cart_item = CartItem.objects.get(pk=item_id, user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Элемент корзины не найден"}, status=status.HTTP_404_NOT_FOUND)
        
        # Получаем новое количество из запроса
        try:
            new_quantity = int(request.data.get('quantity', 1))
        except ValueError:
            return Response({"error": "Количество должно быть целым числом"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем корректность количества
        if new_quantity <= 0:
            return Response({"error": "Количество должно быть положительным числом"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем наличие достаточного количества мест
        performance_schedule = cart_item.performance_schedule
        
        # Если увеличиваем количество, проверяем доступность мест
        if new_quantity > cart_item.quantity:
            additional_seats = new_quantity - cart_item.quantity
            
            if performance_schedule.available_seats < additional_seats:
                return Response({
                    "error": f"Недостаточно мест. Доступно: {performance_schedule.available_seats}, "
                             f"запрошено дополнительно: {additional_seats}"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Обновляем количество
        cart_item.quantity = new_quantity
        cart_item.save()
        
        # Возвращаем обновленный объект
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cart_remove(request, item_id):
    """
    Удаление элемента из корзины
    """
    try:
        cart_item = CartItem.objects.get(id=item_id, user=request.user)
    except CartItem.DoesNotExist:
        return Response({"error": "Элемент корзины не найден"}, status=status.HTTP_404_NOT_FOUND)
    
    cart_item.delete()
    return Response({"message": "Элемент удален из корзины"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cart_clear(request):
    """
    Очистка корзины текущего пользователя
    """
    CartItem.objects.filter(user=request.user).delete()
    return Response({"message": "Корзина очищена"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    """
    Получение списка заказов текущего пользователя
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """
    Получение детальной информации о заказе
    """
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Заказ не найден"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Создание заказа на основе корзины
    """
    serializer = OrderCreateSerializer(data=request.data, context={"request": request})
    
    if serializer.is_valid():
        try:
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    """
    Отмена заказа
    """
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Заказ не найден"}, status=status.HTTP_404_NOT_FOUND)
    
    # Проверяем, можно ли отменить заказ
    if order.status == OrderStatus.COMPLETED:
        return Response({"error": "Нельзя отменить выполненный заказ"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Отменяем заказ
    if order.cancel():
        return Response(OrderSerializer(order).data)
    else:
        return Response({"error": "Ошибка при отмене заказа"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """
    Обновление статуса заказа (только для администраторов)
    """
    if not request.user.is_staff:
        return Response({"error": "Только администратор может обновлять статус заказа"}, 
                        status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Заказ не найден"}, status=status.HTTP_404_NOT_FOUND)
    
    # Получаем новый статус из запроса
    new_status = request.data.get('status')
    if not new_status or new_status not in OrderStatus.values:
        return Response({"error": "Указан неверный статус"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Если заказ был отменен, и теперь его пытаются восстановить
    if order.status == OrderStatus.CANCELLED and new_status != OrderStatus.CANCELLED:
        # Проверяем наличие мест для всех элементов заказа
        for item in order.items.all():
            if item.performance_schedule.available_seats < item.quantity:
                return Response({
                    "error": f"Недостаточно мест для '{item.performance_schedule.performance.name}'. "
                             f"Доступно: {item.performance_schedule.available_seats}, "
                             f"требуется: {item.quantity}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Бронируем места
            item.performance_schedule.reserve_seats(item.quantity)
    
    # Если заказ не был отменен, и теперь его отменяют
    elif order.status != OrderStatus.CANCELLED and new_status == OrderStatus.CANCELLED:
        # Возвращаем места
        for item in order.items.all():
            item.performance_schedule.release_seats(item.quantity)
    
    # Обновляем статус
    order.status = new_status
    order.save()
    
    return Response(OrderSerializer(order).data)


@api_view(['GET'])
def performance_schedules(request, pk):
    """
    Получение всех расписаний для конкретного спектакля
    """
    try:
        schedules = PerformanceSchedule.objects.filter(performance_id=pk)
        serializer = PerformanceScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Представления для каталога

class CatalogCategoryListView(ListAPIView):
    """
    Представление для списка всех категорий спектаклей
    используется как верхний уровень каталога
    """
    queryset = PerformanceCategory.objects.annotate(
        performances_count=Count('performances')
    ).filter(performances_count__gt=0)
    serializer_class = CategoryBriefSerializer
    permission_classes = [AllowAny]


class CatalogCategoryDetailView(RetrieveAPIView):
    """
    Представление для детальной информации о категории
    и всех спектаклях в ней
    """
    queryset = PerformanceCategory.objects.all()
    serializer_class = CategoryWithPerformancesSerializer
    permission_classes = [AllowAny]


class CatalogFeaturedView(APIView):
    """
    Представление для главной страницы каталога
    с подборками спектаклей
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Получаем текущую дату и время
        now = timezone.now()
        
        # Последние добавленные спектакли
        latest_performances = Performance.objects.order_by('-created_at')[:6]
        latest_serializer = PerformanceBriefSerializer(latest_performances, many=True)
        
        # Популярные спектакли (с наибольшим количеством отзывов)
        popular_performances = Performance.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:6]
        popular_serializer = PerformanceBriefSerializer(popular_performances, many=True)
        
        # Ближайшие по дате спектакли
        upcoming_schedules = PerformanceSchedule.objects.filter(
            date_time__gt=now
        ).order_by('date_time')[:10]
        upcoming_performances = list({schedule.performance for schedule in upcoming_schedules})[:6]
        upcoming_serializer = PerformanceBriefSerializer(upcoming_performances, many=True)
        
        # Спектакли с самыми низкими ценами
        budget_performances = Performance.objects.annotate(
            min_price=Min('schedule__price')
        ).order_by('min_price')[:6]
        budget_serializer = PerformanceBriefSerializer(budget_performances, many=True)
        
        # Все категории
        categories = PerformanceCategory.objects.annotate(
            performances_count=Count('performances')
        ).filter(performances_count__gt=0)
        categories_serializer = CategoryBriefSerializer(categories, many=True)
        
        return Response({
            'latest_performances': latest_serializer.data,
            'popular_performances': popular_serializer.data,
            'upcoming_performances': upcoming_serializer.data,
            'budget_performances': budget_serializer.data,
            'categories': categories_serializer.data
        })


class CatalogSearchView(ListAPIView):
    """
    Представление для поиска по каталогу спектаклей
    с расширенными возможностями поиска
    """
    serializer_class = PerformanceBriefSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PerformanceFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = Performance.objects.all()
        
        # Поиск по ключевому слову в имени или описании
        keyword = self.request.query_params.get('keyword', None)
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) | Q(description__icontains=keyword)
            )
        
        # Фильтр по категории
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Фильтр по доступности мест (мин. количество)
        min_seats = self.request.query_params.get('min_seats', None)
        if min_seats:
            queryset = queryset.filter(schedule__available_seats__gte=min_seats).distinct()
        
        # Фильтр по диапазону цен
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(schedule__price__gte=min_price).distinct()
        if max_price:
            queryset = queryset.filter(schedule__price__lte=max_price).distinct()
        
        # Фильтр по дате
        date_after = self.request.query_params.get('date_after', None)
        date_before = self.request.query_params.get('date_before', None)
        if date_after:
            queryset = queryset.filter(schedule__date_time__gte=date_after).distinct()
        if date_before:
            queryset = queryset.filter(schedule__date_time__lte=date_before).distinct()
        
        return queryset


class CatalogStatsView(APIView):
    """
    Представление для получения статистики каталога
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Общее количество спектаклей
        total_performances = Performance.objects.count()
        
        # Общее количество запланированных показов
        now = timezone.now()
        upcoming_shows = PerformanceSchedule.objects.filter(date_time__gt=now).count()
        
        # Количество категорий с наличием спектаклей
        categories_with_performances = PerformanceCategory.objects.annotate(
            performances_count=Count('performances')
        ).filter(performances_count__gt=0).count()
        
        # Диапазон цен
        price_range = PerformanceSchedule.objects.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price')
        )
        
        # Статистика по отзывам
        reviews_stats = Review.objects.aggregate(
            total_reviews=Count('id'),
            total_likes=Count('likes')
        )
        
        return Response({
            'total_performances': total_performances,
            'upcoming_shows': upcoming_shows, 
            'categories_count': categories_with_performances,
            'price_range': {
                'min': float(price_range['min_price']) if price_range['min_price'] else 0,
                'max': float(price_range['max_price']) if price_range['max_price'] else 0,
                'avg': float(price_range['avg_price']) if price_range['avg_price'] else 0
            },
            'reviews_stats': {
                'total': reviews_stats['total_reviews'],
                'likes': reviews_stats['total_likes']
            }
        })



