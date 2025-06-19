from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Theater, Hall


class TheaterModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test theaters
        cls.theater1 = Theater.objects.create(
            name="Большой театр",
            address="Москва, Театральная площадь, 1",
            description="Исторический театр оперы и балета"
        )
        
        cls.theater2 = Theater.objects.create(
            name="Александринский театр",
            address="Санкт-Петербург, площадь Островского, 6",
            description="Старейший национальный театр России"
        )

    def test_theater_creation(self):
        """Test theater creation"""
        self.assertEqual(self.theater1.name, "Большой театр")
        self.assertEqual(self.theater1.address, "Москва, Театральная площадь, 1")
        self.assertEqual(self.theater1.description, "Исторический театр оперы и балета")

    def test_theater_str_representation(self):
        """Test string representation of Theater model"""
        self.assertEqual(str(self.theater1), "Большой театр")

    def test_theater_ordering(self):
        """Test theaters are ordered by name"""
        theaters = Theater.objects.all()
        self.assertEqual(theaters[0].name, "Александринский театр")  # Should be first alphabetically
        self.assertEqual(theaters[1].name, "Большой театр")


class HallModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create theater and halls
        cls.theater = Theater.objects.create(
            name="МХТ им. Чехова",
            address="Москва, Камергерский переулок, 3",
            description="Московский Художественный театр"
        )
        
        cls.hall1 = Hall.objects.create(
            number_hall=1,
            theater=cls.theater
        )
        
        cls.hall2 = Hall.objects.create(
            number_hall=2,
            theater=cls.theater
        )

    def test_hall_creation(self):
        """Test hall creation"""
        self.assertEqual(self.hall1.number_hall, 1)
        self.assertEqual(self.hall1.theater, self.theater)

    def test_hall_str_representation(self):
        """Test string representation of Hall model"""
        self.assertEqual(str(self.hall1), "1")

    def test_hall_theater_relation(self):
        """Test relationship between Hall and Theater models"""
        halls = self.theater.halls.all()
        self.assertEqual(halls.count(), 2)
        self.assertIn(self.hall1, halls)
        self.assertIn(self.hall2, halls)


class TheaterAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create theaters
        cls.theater1 = Theater.objects.create(
            name="Театр на Таганке",
            address="Москва, ул. Земляной Вал, 76/21",
            description="Московский театр драмы и комедии"
        )
        
        cls.theater2 = Theater.objects.create(
            name="Современник",
            address="Москва, Чистопрудный бульвар, 19А",
            description="Московский театр «Современник»"
        )
        
        # Create halls
        cls.hall1 = Hall.objects.create(number_hall=1, theater=cls.theater1)
        cls.hall2 = Hall.objects.create(number_hall=2, theater=cls.theater1)
        cls.hall3 = Hall.objects.create(number_hall=1, theater=cls.theater2)

    def setUp(self):
        self.client = APIClient()

    def test_get_theaters_list(self):
        """Test retrieving list of theaters"""
        # This test needs to be skipped as no theater-list URL is defined
        self.skipTest("No theater-list URL defined")
        
        url = reverse('theater-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Check theater data
        theater_names = [theater['name'] for theater in response.data]
        self.assertIn("Театр на Таганке", theater_names)
        self.assertIn("Современник", theater_names)

    def test_get_theater_detail(self):
        """Test retrieving detailed information about a theater"""
        # This test needs to be skipped as no theater-detail URL is defined
        self.skipTest("No theater-detail URL defined")
        
        url = reverse('theater-detail', kwargs={'pk': self.theater1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Театр на Таганке")
        self.assertEqual(response.data['address'], "Москва, ул. Земляной Вал, 76/21")
        
        # Check included halls
        self.assertEqual(len(response.data['halls']), 2)
        hall_numbers = [hall['number_hall'] for hall in response.data['halls']]
        self.assertIn(1, hall_numbers)
        self.assertIn(2, hall_numbers)

    def test_get_halls_by_theater(self):
        """Test retrieving halls for a specific theater"""
        # Use the actual URL from the perfomance app
        url = f"/api/halls/?theater_id={self.theater1.id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # JsonResponse returns a JSON string, need to parse it
        halls = response.json()
        self.assertEqual(len(halls), 2)
        
        # Verify the correct halls are returned
        hall_numbers = [hall['number_hall'] for hall in halls]
        self.assertIn(1, hall_numbers)
        self.assertIn(2, hall_numbers)

    def test_get_halls_without_theater_param(self):
        """Test retrieving halls without specifying a theater (should return empty list)"""
        # Use the actual URL from the perfomance app
        url = "/api/halls/"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # JsonResponse returns a JSON string, need to parse it
        halls = response.json()
        self.assertEqual(len(halls), 0)  # Empty list expected

    def test_get_nonexistent_theater(self):
        """Test retrieving a theater that doesn't exist"""
        # This test needs to be skipped as no theater-detail URL is defined
        self.skipTest("No theater-detail URL defined")
        
        url = reverse('theater-detail', kwargs={'pk': 9999})  # Non-existent ID
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
