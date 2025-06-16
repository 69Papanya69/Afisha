from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate
from decimal import Decimal
import datetime
from rest_framework import serializers

from perfomance.serializers import OrderCreateSerializer
from perfomance.models import Performance, PerformanceSchedule, CartItem, Order
from main.models import Theater, Hall
from perfomance.views import create_order

User = get_user_model()

class OrderCreateSerializerTest(TestCase):
    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Создаем театр и зал
        self.theater = Theater.objects.create(
            name='Test Theater',
            address='Test Address',
            description='Test Description'
        )
        self.hall = Hall.objects.create(
            theater=self.theater,
            number_hall=1
        )
        
        # Создаем спектакль и расписание
        self.performance = Performance.objects.create(
            name='Test Performance',
            description='Test Description',
            duration_time=datetime.timedelta(hours=1, minutes=30)
        )
        
        self.schedule = PerformanceSchedule.objects.create(
            performance=self.performance,
            theater=self.theater,
            hall=self.hall,
            date_time='2025-01-01T19:00:00Z',
            available_seats=50,
            price=1000
        )
        
        # Создаем запрос для тестирования
        self.factory = APIRequestFactory()
        
    def test_validate_delivery_address_valid(self):
        """Тест валидной адресной строки"""
        valid_addresses = [
            "ул. Пушкина, д. 10, г. Москва, индекс 123456",
            "ул Ленина д 5 г Санкт-Петербург индекс 654321",
            "ул. Гоголя, д. 3, корп. 1, г. Новосибирск, индекс 654321",
        ]
        
        serializer = OrderCreateSerializer()
        
        for address in valid_addresses:
            try:
                result = serializer.validate_delivery_address(address)
                self.assertEqual(result, address)
            except:
                self.fail(f"validate_delivery_address вызвало исключение с валидным адресом: {address}")
    
    def test_validate_delivery_address_invalid(self):
        """Тест невалидной адресной строки"""
        serializer = OrderCreateSerializer()
        
        # Проверяем один конкретный случай без индекса
        invalid_address = "ул. Пушкина, д. 10, г. Москва"
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_delivery_address(invalid_address)
    
    def test_validate_amount_limits(self):
        """Тест лимитов на суммы заказа"""
        # Создаем элемент корзины с низкой стоимостью
        low_price_schedule = PerformanceSchedule.objects.create(
            performance=self.performance,
            theater=self.theater,
            hall=self.hall,
            date_time='2025-01-02T19:00:00Z',
            available_seats=50,
            price=100  # Цена 100 рублей
        )
        
        # Создаем элемент корзины с высокой стоимостью
        high_price_schedule = PerformanceSchedule.objects.create(
            performance=self.performance,
            theater=self.theater,
            hall=self.hall,
            date_time='2025-01-03T19:00:00Z',
            available_seats=50,
            price=50000  # Цена 50 000 рублей
        )
        
        # Очищаем корзину пользователя
        CartItem.objects.filter(user=self.user).delete()
        
        # Тест на низкую сумму
        CartItem.objects.create(
            user=self.user,
            performance_schedule=low_price_schedule,
            quantity=4  # 4 * 100 = 400 рублей (ниже минимума в 500)
        )
        
        data = {
            'customer_name': 'Test Customer',
            'customer_email': 'test@example.com',
            'customer_phone': '123456789',
            'payment_method': 'Онлайн'
        }
        
        request = self.factory.post(reverse('order-create'))
        force_authenticate(request, user=self.user)
        request.user = self.user
        
        serializer = OrderCreateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertTrue(any('Минимальная сумма заказа' in error for error in serializer.errors['non_field_errors']))
        
        # Очищаем корзину пользователя
        CartItem.objects.filter(user=self.user).delete()
        
        # Тест на высокую сумму
        CartItem.objects.create(
            user=self.user,
            performance_schedule=high_price_schedule,
            quantity=3  # 3 * 50000 = 150 000 рублей (выше максимума в 100 000)
        )
        
        serializer = OrderCreateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertTrue(any('Максимальная сумма заказа' in error for error in serializer.errors['non_field_errors']))
        
        # Очищаем корзину пользователя
        CartItem.objects.filter(user=self.user).delete()
        
        # Тест на валидную сумму
        CartItem.objects.create(
            user=self.user,
            performance_schedule=self.schedule,
            quantity=1  # 1 * 1000 = 1000 рублей (в пределах от 500 до 100 000)
        )
        
        serializer = OrderCreateSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
    
    def test_validate_seats_availability(self):
        """Тест на доступность мест"""
        # Создаем расписание с ограниченным количеством мест
        limited_seats_schedule = PerformanceSchedule.objects.create(
            performance=self.performance,
            theater=self.theater,
            hall=self.hall,
            date_time='2025-01-04T19:00:00Z',
            available_seats=5,  # Только 5 доступных мест
            price=1000
        )
        
        # Очищаем корзину пользователя
        CartItem.objects.filter(user=self.user).delete()
        
        # Пытаемся добавить слишком много мест
        CartItem.objects.create(
            user=self.user,
            performance_schedule=limited_seats_schedule,
            quantity=10  # Запрашиваем 10 мест, но доступно только 5
        )
        
        data = {
            'customer_name': 'Test Customer',
            'customer_email': 'test@example.com',
            'customer_phone': '123456789',
            'payment_method': 'Онлайн'
        }
        
        request = self.factory.post(reverse('order-create'))
        force_authenticate(request, user=self.user)
        request.user = self.user
        
        serializer = OrderCreateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertTrue(any('Недостаточно мест' in error for error in serializer.errors['non_field_errors']))
        
        # Очищаем корзину пользователя
        CartItem.objects.filter(user=self.user).delete()
        
        # Добавляем корректное количество мест
        CartItem.objects.create(
            user=self.user,
            performance_schedule=limited_seats_schedule,
            quantity=3  # Запрашиваем 3 места из 5 доступных
        )
        
        serializer = OrderCreateSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid()) 