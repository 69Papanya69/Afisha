from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from perfomance.models import (
    Performance, PerformanceCategory, PerformanceSchedule,
    Review, CartItem, Order, OrderStatus, OrderItem
)
from main.models import Theater, Hall
from users.models import User


class PerformanceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a category
        cls.category = PerformanceCategory.objects.create(
            name="Драма",
            description="Драматические постановки"
        )
        
        # Create a performance
        cls.performance = Performance.objects.create(
            name="Ревизор",
            description="Комедия Н.В. Гоголя",
            duration_time=timedelta(hours=2, minutes=30),
            category=cls.category
        )

    def test_performance_str_representation(self):
        self.assertEqual(str(self.performance), "Ревизор")

    def test_performance_get_absolute_url(self):
        url = self.performance.get_absolute_url()
        self.assertEqual(url, f'/api/performances/{self.performance.id}/')

    def test_performance_category_relation(self):
        self.assertEqual(self.performance.category, self.category)


class PerformanceScheduleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create theater, hall, category and performance
        cls.theater = Theater.objects.create(
            name="Большой театр",
            address="Москва, Театральная площадь, 1",
            description="Исторический театр оперы и балета"
        )
        
        cls.hall = Hall.objects.create(
            number_hall=1,
            theater=cls.theater
        )
        
        cls.category = PerformanceCategory.objects.create(
            name="Балет",
            description="Балетные постановки"
        )
        
        cls.performance = Performance.objects.create(
            name="Лебединое озеро",
            description="Балет П.И. Чайковского",
            duration_time=timedelta(hours=2, minutes=45),
            category=cls.category
        )
        
        # Create schedule
        cls.schedule = PerformanceSchedule.objects.create(
            performance=cls.performance,
            theater=cls.theater,
            hall=cls.hall,
            date_time=timezone.now() + timedelta(days=1),
            available_seats=100,
            price=Decimal('1500.00')
        )

    def test_schedule_str_representation(self):
        expected_str = f"{self.performance.name} - {self.schedule.date_time}"
        self.assertEqual(str(self.schedule), expected_str)

    def test_reserve_seats_success(self):
        initial_seats = self.schedule.available_seats
        seats_to_reserve = 5
        
        result = self.schedule.reserve_seats(seats_to_reserve)
        
        # Refresh from database
        self.schedule.refresh_from_db()
        
        # Check result and available seats
        self.assertTrue(result)
        self.assertEqual(self.schedule.available_seats, initial_seats - seats_to_reserve)

    def test_reserve_seats_failure(self):
        self.schedule.available_seats = 3
        self.schedule.save()
        
        # Try to reserve more seats than available
        result = self.schedule.reserve_seats(5)
        
        # Refresh from database
        self.schedule.refresh_from_db()
        
        # Check result and available seats (should remain unchanged)
        self.assertFalse(result)
        self.assertEqual(self.schedule.available_seats, 3)

    def test_release_seats(self):
        initial_seats = 50
        self.schedule.available_seats = initial_seats
        self.schedule.save()
        
        seats_to_release = 10
        self.schedule.release_seats(seats_to_release)
        
        # Refresh from database
        self.schedule.refresh_from_db()
        
        # Check available seats
        self.assertEqual(self.schedule.available_seats, initial_seats + seats_to_release)


class OrderModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create theater, hall, category and performance
        cls.theater = Theater.objects.create(
            name="Современник",
            address="Москва, Чистопрудный бульвар, 19А",
            description="Московский театр"
        )
        
        cls.hall = Hall.objects.create(
            number_hall=2,
            theater=cls.theater
        )
        
        cls.performance = Performance.objects.create(
            name="Вишневый сад",
            description="Пьеса А.П. Чехова",
            duration_time=timedelta(hours=3)
        )
        
        # Create schedule
        cls.schedule = PerformanceSchedule.objects.create(
            performance=cls.performance,
            theater=cls.theater,
            hall=cls.hall,
            date_time=timezone.now() + timedelta(days=2),
            available_seats=150,
            price=Decimal('2000.00')
        )
        
        # Create order
        cls.order = Order.objects.create(
            user=cls.user,
            status=OrderStatus.PENDING,
            total_amount=Decimal('6000.00'),
            customer_name='Иван Иванов',
            customer_email='ivan@example.com',
            customer_phone='+7-999-123-45-67',
            payment_method='Банковская карта'
        )
        
        # Create order item
        cls.order_item = OrderItem.objects.create(
            order=cls.order,
            performance_schedule=cls.schedule,
            quantity=3,
            price_per_unit=Decimal('2000.00')
        )

    def test_order_str_representation(self):
        expected_str = f"Заказ #{self.order.id} ({self.user.username})"
        self.assertEqual(str(self.order), expected_str)

    def test_order_calculate_total(self):
        total = self.order.calculate_total()
        expected_total = Decimal('6000.00')  # 3 tickets * 2000
        self.assertEqual(total, expected_total)

    def test_order_cancel_success(self):
        # Check initial state
        self.assertEqual(self.order.status, OrderStatus.PENDING)
        initial_seats = self.schedule.available_seats
        
        # Cancel order
        result = self.order.cancel()
        
        # Refresh from database
        self.order.refresh_from_db()
        self.schedule.refresh_from_db()
        
        # Check status and available seats
        self.assertTrue(result)
        self.assertEqual(self.order.status, OrderStatus.CANCELLED)
        self.assertEqual(self.schedule.available_seats, initial_seats + self.order_item.quantity)

    def test_order_cancel_already_cancelled(self):
        # Set order as already cancelled
        self.order.status = OrderStatus.CANCELLED
        self.order.save()
        
        # Try to cancel again
        result = self.order.cancel()
        
        # Should return False
        self.assertFalse(result)


class CartItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create user
        cls.user = User.objects.create_user(
            username='cartuser',
            email='cart@example.com',
            password='cartpass123'
        )
        
        # Create performance and schedule
        cls.theater = Theater.objects.create(name="Театр на Таганке", address="Москва")
        cls.hall = Hall.objects.create(number_hall=1, theater=cls.theater)
        
        cls.performance = Performance.objects.create(
            name="Гамлет",
            description="Трагедия У. Шекспира",
            duration_time=timedelta(hours=3, minutes=15)
        )
        
        cls.schedule = PerformanceSchedule.objects.create(
            performance=cls.performance,
            theater=cls.theater,
            hall=cls.hall,
            date_time=timezone.now() + timedelta(days=3),
            available_seats=80,
            price=Decimal('1800.00')
        )
        
        # Create cart item
        cls.cart_item = CartItem.objects.create(
            user=cls.user,
            performance_schedule=cls.schedule,
            quantity=2
        )

    def test_cart_item_str_representation(self):
        expected_str = f"{self.user.username} - {self.performance.name} ({self.cart_item.quantity})"
        self.assertEqual(str(self.cart_item), expected_str)

    def test_cart_item_total_price(self):
        expected_total = Decimal('3600.00')  # 2 tickets * 1800
        self.assertEqual(self.cart_item.total_price, expected_total) 