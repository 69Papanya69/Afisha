from django.test import TestCase
from .models import User

class UserModelTest(TestCase):
    """Тесты для модели пользователя"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertEqual(str(self.user), 'testuser')
    
    def test_get_profile_image_url(self):
        """Тест получения URL изображения профиля"""
        # Проверяем, что метод возвращает дефолтное изображение, если профильное не установлено
        self.assertTrue('default_profile_image.png' in self.user.get_profile_image_url()) 