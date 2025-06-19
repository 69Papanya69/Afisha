from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from datetime import timedelta
from decimal import Decimal
import json

from perfomance.models import (
    Performance, PerformanceCategory, PerformanceSchedule,
    Review, Order, OrderStatus, CartItem
)
from main.models import Theater, Hall
from users.models import User


class PerformanceAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create categories
        cls.category1 = PerformanceCategory.objects.create(
            name="Комедия",
            description="Комедийные постановки"
        )
        
        cls.category2 = PerformanceCategory.objects.create(
            name="Трагедия",
            description="Трагические постановки"
        )
        
        # Create performances
        cls.performance1 = Performance.objects.create(
            name="Горе от ума",
            description="Комедия А.С. Грибоедова",
            duration_time=timedelta(hours=2, minutes=30),
            category=cls.category1
        )
        
        cls.performance2 = Performance.objects.create(
            name="Король Лир",
            description="Трагедия У. Шекспира",
            duration_time=timedelta(hours=3),
            category=cls.category2
        )
        
        # Create theater and hall
        cls.theater = Theater.objects.create(
            name="МХТ им. Чехова",
            address="Москва, Камергерский переулок, 3",
            description="Московский Художественный театр"
        )
        
        cls.hall = Hall.objects.create(
            number_hall=1,
            theater=cls.theater
        )
        
        # Create schedules
        cls.schedule1 = PerformanceSchedule.objects.create(
            performance=cls.performance1,
            theater=cls.theater,
            hall=cls.hall,
            date_time=timezone.now() + timedelta(days=1),
            available_seats=100,
            price=Decimal('1500.00')
        )
        
        cls.schedule2 = PerformanceSchedule.objects.create(
            performance=cls.performance2,
            theater=cls.theater,
            hall=cls.hall,
            date_time=timezone.now() + timedelta(days=2),
            available_seats=120,
            price=Decimal('2000.00')
        )
        
        # URL for performance list
        cls.performance_list_url = reverse('performance-list')

    def test_get_performance_list(self):
        """Test retrieving all performances"""
        response = self.client.get(self.performance_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_get_performance_detail(self):
        """Test retrieving a single performance"""
        url = reverse('performance_detail', kwargs={'pk': self.performance1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.performance1.name)
    
    def test_filter_performances_by_category(self):
        """Test filtering performances by category"""
        # Use the filter view instead
        url = f"{reverse('performance-filter')}?category={self.category1.id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.performance1.name)


class CartAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create performance, theater, hall, and schedule
        cls.theater = Theater.objects.create(name="Театр Сатиры", address="Москва")
        cls.hall = Hall.objects.create(number_hall=1, theater=cls.theater)
        
        cls.performance = Performance.objects.create(
            name="Ревизор",
            description="Комедия Н.В. Гоголя",
            duration_time=timedelta(hours=2, minutes=15)
        )
        
        cls.schedule = PerformanceSchedule.objects.create(
            performance=cls.performance,
            theater=cls.theater,
            hall=cls.hall,
            date_time=timezone.now() + timedelta(days=1),
            available_seats=80,
            price=Decimal('1200.00')
        )
        
        # URLs
        cls.cart_list_url = reverse('cart-list')
        cls.cart_add_url = reverse('cart-add')
        cls.cart_clear_url = reverse('cart-clear')

    def setUp(self):
        # Setup runs before each test
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_cart_list_empty(self):
        """Test retrieving an empty cart"""
        response = self.client.get(self.cart_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_add_to_cart(self):
        """Test adding an item to the cart"""
        data = {
            'performance_schedule_id': self.schedule.id,
            'quantity': 2
        }
        
        response = self.client.post(self.cart_add_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check cart now has the item
        response = self.client.get(self.cart_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['quantity'], 2)
    
    def test_update_cart_quantity(self):
        """Test updating quantity of a cart item"""
        # First add an item
        cart_item = CartItem.objects.create(
            user=self.user,
            performance_schedule=self.schedule,
            quantity=1
        )
        
        # Now update the quantity
        update_url = reverse('cart-update-quantity', kwargs={'item_id': cart_item.id})
        data = {'quantity': 3}
        
        response = self.client.post(update_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check cart now has updated quantity
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)
    
    def test_remove_from_cart(self):
        """Test removing an item from the cart"""
        # First add an item
        cart_item = CartItem.objects.create(
            user=self.user,
            performance_schedule=self.schedule,
            quantity=2
        )
        
        # Now remove it
        remove_url = reverse('cart-remove', kwargs={'item_id': cart_item.id})
        response = self.client.delete(remove_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check cart is now empty
        self.assertEqual(CartItem.objects.count(), 0)
    
    def test_clear_cart(self):
        """Test clearing the entire cart"""
        # Add multiple items to cart
        CartItem.objects.create(
            user=self.user,
            performance_schedule=self.schedule,
            quantity=2
        )
        
        # Create another schedule and add to cart
        schedule2 = PerformanceSchedule.objects.create(
            performance=self.performance,
            theater=self.theater,
            hall=self.hall,
            date_time=timezone.now() + timedelta(days=2),
            available_seats=70,
            price=Decimal('1500.00')
        )
        
        CartItem.objects.create(
            user=self.user,
            performance_schedule=schedule2,
            quantity=1
        )
        
        # Verify we have 2 items
        self.assertEqual(CartItem.objects.count(), 2)
        
        # Clear the cart
        response = self.client.post(self.cart_clear_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check cart is now empty
        self.assertEqual(CartItem.objects.count(), 0)


class OrderAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create user
        cls.user = User.objects.create_user(
            username='orderuser',
            email='order@example.com',
            password='orderpass123'
        )
        
        # Create performance, theater, hall, and schedule
        cls.theater = Theater.objects.create(name="Театр на Малой Бронной", address="Москва")
        cls.hall = Hall.objects.create(number_hall=1, theater=cls.theater)
        
        cls.performance = Performance.objects.create(
            name="Три сестры",
            description="Пьеса А.П. Чехова",
            duration_time=timedelta(hours=3, minutes=30)
        )
        
        cls.schedule = PerformanceSchedule.objects.create(
            performance=cls.performance,
            theater=cls.theater,
            hall=cls.hall,
            date_time=timezone.now() + timedelta(days=3),
            available_seats=100,
            price=Decimal('2000.00')
        )
        
        # Add an item to cart
        cls.cart_item = CartItem.objects.create(
            user=cls.user,
            performance_schedule=cls.schedule,
            quantity=2
        )
        
        # URLs
        cls.order_list_url = reverse('order-list')
        cls.create_order_url = reverse('order-create')

    def setUp(self):
        # Setup runs before each test
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_order_from_cart(self):
        """Test creating an order from cart items"""
        data = {
            'customer_name': 'Иван Петров',
            'customer_email': 'ivan@example.com',
            'customer_phone': '+7-999-888-77-66',
            'payment_method': 'Банковская карта'
        }
        
        response = self.client.post(self.create_order_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify order was created
        self.assertEqual(Order.objects.count(), 1)
        
        # Verify cart is now empty
        self.assertEqual(CartItem.objects.count(), 0)
        
        # Verify order details
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(order.customer_name, 'Иван Петров')
        
        # Check order items
        self.assertEqual(order.items.count(), 1)
        order_item = order.items.first()
        self.assertEqual(order_item.performance_schedule, self.schedule)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price_per_unit, Decimal('2000.00'))
    
    def test_cancel_order(self):
        """Test cancelling an order"""
        # Create an order
        order = Order.objects.create(
            user=self.user,
            status=OrderStatus.PENDING,
            total_amount=Decimal('4000.00'),
            customer_name='Петр Иванов',
            customer_email='petr@example.com',
            customer_phone='+7-999-111-22-33',
            payment_method='Наличные'
        )
        
        # Reduce available seats
        self.schedule.available_seats = 98  # 100 - 2
        self.schedule.save()
        
        # Create order item
        from perfomance.models import OrderItem
        OrderItem.objects.create(
            order=order,
            performance_schedule=self.schedule,
            quantity=2,
            price_per_unit=Decimal('2000.00')
        )
        
        # Cancel the order
        cancel_url = reverse('order-cancel', kwargs={'order_id': order.id})
        response = self.client.post(cancel_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify order status is CANCELLED
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.CANCELLED)
        
        # Verify seats were released
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.available_seats, 100)  # Back to original 100 