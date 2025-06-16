from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.utils import timezone
from datetime import timedelta

from .models import Question, Answer
from users.models import User
from .serializers import QuestionSerializer


class QuestionModelTest(TestCase):
    """Тесты модели вопросов"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='questioner',
            email='questioner@example.com',
            password='questionpass'
        )
        self.question = Question.objects.create(
            user=self.user,
            text='Какие спектакли идут в этом месяце?'
        )
    
    def test_question_creation(self):
        """Тест создания объекта вопроса"""
        self.assertEqual(self.question.user, self.user)
        self.assertEqual(self.question.text, 'Какие спектакли идут в этом месяце?')
        self.assertTrue(hasattr(self.question, 'created_at'))
        self.assertEqual(str(self.question), f"Question by {self.user.username}")


class AnswerModelTest(TestCase):
    """Тесты модели ответов"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='questioner',
            email='questioner@example.com',
            password='questionpass'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            is_staff=True
        )
        self.question = Question.objects.create(
            user=self.user,
            text='Какие спектакли идут в этом месяце?'
        )
        self.answer = Answer.objects.create(
            question=self.question,
            user=self.admin,
            text='В этом месяце у нас идут "Гамлет", "Лебединое озеро" и "Кармен".'
        )
    
    def test_answer_creation(self):
        """Тест создания объекта ответа"""
        self.assertEqual(self.answer.question, self.question)
        self.assertEqual(self.answer.user, self.admin)
        self.assertEqual(self.answer.text, 'В этом месяце у нас идут "Гамлет", "Лебединое озеро" и "Кармен".')
        self.assertTrue(hasattr(self.answer, 'created_at'))
        self.assertEqual(str(self.answer), f"Answer by {self.admin.username} to {self.question.id}")


class QuestionAPITest(APITestCase):
    """Тесты API для вопросов"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаем пользователей
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='user2pass'
        )
        
        # Создаем вопросы с разным временем создания
        self.question1 = Question.objects.create(
            user=self.user1,
            text='Как купить билеты онлайн?'
        )
        
        # Создаем вопрос, созданный "вчера"
        self.question2 = Question.objects.create(
            user=self.user2,
            text='Какие мероприятия будут в следующем сезоне?'
        )
        Question.objects.filter(pk=self.question2.pk).update(
            created_at=timezone.now() - timedelta(days=1)
        )
        
        # Создаем вопрос, созданный "позавчера"
        self.question3 = Question.objects.create(
            user=self.user1,
            text='Можно ли вернуть билет?'
        )
        Question.objects.filter(pk=self.question3.pk).update(
            created_at=timezone.now() - timedelta(days=2)
        )
        
        # Создаем вопрос, созданный "3 дня назад"
        self.question4 = Question.objects.create(
            user=self.user2,
            text='Где находится ваш театр?'
        )
        Question.objects.filter(pk=self.question4.pk).update(
            created_at=timezone.now() - timedelta(days=3)
        )
    
    def test_last_questions_view(self):
        """Тест представления последних 3х вопросов"""
        url = reverse('question-last')  # Используем правильное имя URL-шаблона
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Проверяем, что вопросы отсортированы по дате создания (сначала новые)
        self.assertEqual(response.data[0]['id'], self.question1.id)
        self.assertEqual(response.data[1]['id'], self.question2.id)
        self.assertEqual(response.data[2]['id'], self.question3.id)
        
        # Проверяем, что старый вопрос не включен в результат
        for item in response.data:
            self.assertNotEqual(item['id'], self.question4.id)
