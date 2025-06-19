from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from decimal import Decimal

from perfomance.models import (
    Performance, PerformanceCategory, PerformanceSchedule,
    Review, Order, OrderStatus, OrderItem, CartItem
)
from main.models import Theater, Hall
from users.models import User


class TicketOrderFlowTest(TestCase):
    """
    Test the entire flow from browsing performances to completing an order
    """
    
    @classmethod
    def setUpTestData(cls):
        # Create test data
        # 1. Create a user
        cls.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='customerpass123'
        )
        
        # 2. Create categories
        cls.category = PerformanceCategory.objects.create(
            name="Мюзикл",
            description="Музыкально-драматические представления"
        )
        
        # 3. Create theater and hall
        cls.theater = Theater.objects.create(
            name="Театр мюзикла",
            address="Москва, Большая Дмитровка, 17",
            description="Московский театр мюзикла"
        )
        
        cls.hall = Hall.objects.create(
            number_hall=1,
            theater=cls.theater
        )
        
        # 4. Create performances
        cls.performance1 = Performance.objects.create(
            name="Призрак оперы",
            description="Мюзикл Эндрю Ллойда Уэббера",
            duration_time=timedelta(hours=2, minutes=45),
            category=cls.category
        )
        
        cls.performance2 = Performance.objects.create(
            name="Кошки",
            description="Знаменитый мюзикл о кошках",
            duration_time=timedelta(hours=2, minutes=30),
            category=cls.category
        )
        
        # 5. Create schedules
        cls.schedule1 = PerformanceSchedule.objects.create(
            performance=cls.performance1,
            theater=cls.theater,
            hall=cls.hall,
            date_time=timezone.now() + timedelta(days=5),
            available_seats=50,
            price=Decimal('2500.00')
        )
        
        cls.schedule2 = PerformanceSchedule.objects.create(
            performance=cls.performance2,
            theater=cls.theater,
            hall=cls.hall,
            date_time=timezone.now() + timedelta(days=7),
            available_seats=60,
            price=Decimal('2000.00')
        )

    def setUp(self):
        # Setup for each test
        self.client = APIClient()
        # Make sure we force authenticate to avoid 401 errors
        self.client.force_authenticate(user=self.user)

    def test_complete_order_flow(self):
        """
        Test the complete flow of ordering tickets:
        1. Browse performances
        2. View performance details
        3. Add tickets to cart
        4. View cart
        5. Create order
        6. View order details
        """
        
        # 1. Browse performances
        response = self.client.get(reverse('performance-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # 2. View performance details
        detail_url = reverse('performance_detail', kwargs={'pk': self.performance1.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Призрак оперы")
        
        # 3. Add tickets to cart
        cart_add_url = reverse('cart-add')
        cart_data = {
            'performance_schedule_id': self.schedule1.id,
            'quantity': 2
        }
        response = self.client.post(cart_add_url, cart_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 4. View cart
        cart_list_url = reverse('cart-list')
        response = self.client.get(cart_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['quantity'], 2)
        
        # 5. Create order
        create_order_url = reverse('order-create')
        order_data = {
            'customer_name': 'Анна Карелина',
            'customer_email': 'anna@example.com',
            'customer_phone': '+7-999-123-45-67',
            'payment_method': 'Банковская карта'
        }
        response = self.client.post(create_order_url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data['id']
        
        # 6. View order details
        order_detail_url = reverse('order-detail', kwargs={'order_id': order_id})
        response = self.client.get(order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['customer_name'], 'Анна Карелина')
        self.assertEqual(response.data['status'], OrderStatus.PENDING)
        self.assertEqual(len(response.data['items']), 1)
        
        # 7. Verify seats were reserved
        self.schedule1.refresh_from_db()
        self.assertEqual(self.schedule1.available_seats, 48)  # 50 - 2
    
    def test_cancel_order_flow(self):
        """
        Test the flow of cancelling an order:
        1. Create an order
        2. Cancel the order
        3. Verify seats were released
        """
        
        # 1. Add to cart
        cart_add_url = reverse('cart-add')
        cart_data = {
            'performance_schedule_id': self.schedule2.id,
            'quantity': 3
        }
        response = self.client.post(cart_add_url, cart_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Create order
        create_order_url = reverse('order-create')
        order_data = {
            'customer_name': 'Петр Иванов',
            'customer_email': 'petr@example.com',
            'customer_phone': '+7-999-888-77-66',
            'payment_method': 'Наличные'
        }
        response = self.client.post(create_order_url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data['id']
        
        # Verify seats were reserved
        self.schedule2.refresh_from_db()
        self.assertEqual(self.schedule2.available_seats, 57)  # 60 - 3
        
        # 3. Cancel order
        cancel_url = reverse('order-cancel', kwargs={'order_id': order_id})
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Check order status
        order_detail_url = reverse('order-detail', kwargs={'order_id': order_id})
        response = self.client.get(order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], OrderStatus.CANCELLED)
        
        # 5. Verify seats were released
        self.schedule2.refresh_from_db()
        self.assertEqual(self.schedule2.available_seats, 60)  # Back to 60


class ReviewIntegrationTest(TestCase):
    """
    Test the integration between performances and reviews
    """
    
    @classmethod
    def setUpTestData(cls):
        # Create user
        cls.user = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='reviewpass123'
        )
        
        # Create performance
        cls.performance = Performance.objects.create(
            name="Чайка",
            description="Пьеса А.П. Чехова",
            duration_time=timedelta(hours=2, minutes=15)
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_review_lifecycle(self):
        """
        Test the lifecycle of a review:
        1. Add a review
        2. View the review in performance details
        3. Update the review
        4. Delete the review
        """
        
        # 1. Add review
        add_review_url = reverse('add_review', kwargs={'pk': self.performance.id})
        review_data = {
            'text': 'Отличное представление, яркие костюмы, великолепная игра актеров!'
        }
        response = self.client.post(add_review_url, review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review_id = response.data['id']
        
        # 2. View performance details with review
        detail_url = reverse('performance_detail', kwargs={'pk': self.performance.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['reviews']), 1)
        self.assertEqual(response.data['reviews'][0]['text'], review_data['text'])
        
        # 3. Update review
        update_review_url = reverse('update_review', kwargs={'pk': review_id})
        updated_data = {
            'text': 'Обновленный отзыв: очень понравилось представление!'
        }
        response = self.client.put(update_review_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if review was updated
        detail_url = reverse('performance_detail', kwargs={'pk': self.performance.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.data['reviews'][0]['text'], updated_data['text'])
        
        # 4. Delete review
        delete_review_url = reverse('delete_review', kwargs={'pk': review_id})
        response = self.client.delete(delete_review_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check if review was deleted
        detail_url = reverse('performance_detail', kwargs={'pk': self.performance.id})
        response = self.client.get(detail_url)
        self.assertEqual(len(response.data['reviews']), 0) 