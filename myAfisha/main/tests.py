from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Theater, Hall


class TheaterModelTest(TestCase):
    """Тесты модели театра"""
    
    def setUp(self):
        self.theater = Theater.objects.create(
            name='Большой театр',
            address='Москва, Театральная площадь, 1',
            description='Государственный академический Большой театр России'
        )
    
    def test_theater_creation(self):
        """Тест создания объекта театра"""
        self.assertEqual(self.theater.name, 'Большой театр')
        self.assertEqual(self.theater.address, 'Москва, Театральная площадь, 1')
        self.assertEqual(self.theater.description, 'Государственный академический Большой театр России')
        self.assertEqual(str(self.theater), 'Большой театр')


class HallModelTest(TestCase):
    """Тесты модели зала"""
    
    def setUp(self):
        self.theater = Theater.objects.create(
            name='Мариинский театр',
            address='Санкт-Петербург, Театральная площадь, 1',
            description='Государственный академический Мариинский театр'
        )
        self.hall = Hall.objects.create(
            number_hall=1,
            theater=self.theater
        )
    
    def test_hall_creation(self):
        """Тест создания объекта зала"""
        self.assertEqual(self.hall.number_hall, 1)
        self.assertEqual(self.hall.theater, self.theater)
        self.assertEqual(str(self.hall), "1")


class TheaterHallsTest(TestCase):
    """Тесты для связи театров и залов"""
    
    def setUp(self):
        self.theater1 = Theater.objects.create(
            name='МХТ им. Чехова',
            address='Москва, Камергерский переулок, 3',
            description='Московский Художественный театр имени А.П. Чехова'
        )
        self.theater2 = Theater.objects.create(
            name='Малый театр',
            address='Москва, Театральный проезд, 1',
            description='Государственный академический Малый театр'
        )
        
        # Создаем залы для первого театра
        self.hall1_1 = Hall.objects.create(number_hall=1, theater=self.theater1)
        self.hall1_2 = Hall.objects.create(number_hall=2, theater=self.theater1)
        self.hall1_3 = Hall.objects.create(number_hall=3, theater=self.theater1)
        
        # Создаем залы для второго театра
        self.hall2_1 = Hall.objects.create(number_hall=1, theater=self.theater2)
        self.hall2_2 = Hall.objects.create(number_hall=2, theater=self.theater2)
    
    def test_theater_halls_relation(self):
        """Тест связи между театром и залами"""
        # Проверяем кол-во залов в каждом театре
        self.assertEqual(self.theater1.halls.count(), 3)
        self.assertEqual(self.theater2.halls.count(), 2)
        
        # Проверяем номера залов в первом театре
        hall_numbers_theater1 = [hall.number_hall for hall in self.theater1.halls.all()]
        self.assertIn(1, hall_numbers_theater1)
        self.assertIn(2, hall_numbers_theater1)
        self.assertIn(3, hall_numbers_theater1)
        
        # Проверяем номера залов во втором театре
        hall_numbers_theater2 = [hall.number_hall for hall in self.theater2.halls.all()]
        self.assertIn(1, hall_numbers_theater2)
        self.assertIn(2, hall_numbers_theater2)
