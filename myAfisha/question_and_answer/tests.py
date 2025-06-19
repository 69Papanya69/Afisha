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
    
    @classmethod
    def setUpTestData(cls):
        # Create user
        cls.user = User.objects.create_user(
            username='askeruser',
            email='asker@example.com',
            password='askerpass123'
        )
        
        # Create question
        cls.question = Question.objects.create(
            user=cls.user,
            title="Как заказать билеты?",
            content="Подскажите, как заказать билеты на спектакль онлайн?",
            is_answered=False
        )

    def test_question_str_representation(self):
        """Test string representation of Question model"""
        self.assertEqual(str(self.question), "Как заказать билеты?")

    def test_question_creation_date(self):
        """Test question creation date is set correctly"""
        self.assertIsNotNone(self.question.created_at)
        self.assertTrue((timezone.now() - self.question.created_at).seconds < 60)
        
    def test_question_default_values(self):
        """Test default values for question"""
        self.assertFalse(self.question.is_answered)


class AnswerModelTest(TestCase):
    """Тесты модели ответов"""
    
    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.user_asker = User.objects.create_user(
            username='askeruser',
            email='asker@example.com',
            password='askerpass123'
        )
        
        cls.user_answerer = User.objects.create_user(
            username='answereruser',
            email='answerer@example.com',
            password='answererpass123',
            is_staff=True
        )
        
        # Create question
        cls.question = Question.objects.create(
            user=cls.user_asker,
            title="Когда начинается представление?",
            content="В какое время начинается вечернее представление?",
            is_answered=False
        )
        
        # Create answer
        cls.answer = Answer.objects.create(
            question=cls.question,
            user=cls.user_answerer,
            content="Вечернее представление обычно начинается в 19:00."
        )

    def test_answer_str_representation(self):
        """Test string representation of Answer model"""
        expected_str = f"Ответ на: {self.question.title}"
        self.assertEqual(str(self.answer), expected_str)

    def test_question_is_answered_after_answer_created(self):
        """Test question is marked as answered after an answer is created"""
        self.question.refresh_from_db()
        self.assertTrue(self.question.is_answered)

    def test_answer_creation_date(self):
        """Test answer creation date is set correctly"""
        self.assertIsNotNone(self.answer.created_at)
        self.assertTrue((timezone.now() - self.answer.created_at).seconds < 60)


class QuestionAPITest(APITestCase):
    """Тесты API для вопросов"""
    
    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='regularpass123'
        )
        
        cls.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        # Create questions
        cls.question1 = Question.objects.create(
            user=cls.regular_user,
            title="Вопрос о возврате билетов",
            content="Как осуществить возврат билета в случае отмены спектакля?",
            is_answered=False
        )
        
        cls.question2 = Question.objects.create(
            user=cls.regular_user,
            title="Вопрос о скидках",
            content="Есть ли скидки для студентов?",
            is_answered=True
        )
        
        # Create answer for question2
        cls.answer = Answer.objects.create(
            question=cls.question2,
            user=cls.admin_user,
            content="Да, студентам предоставляется скидка 20% при предъявлении студенческого билета."
        )

    def setUp(self):
        self.client = APIClient()

    def test_list_questions_unauthenticated(self):
        """Test listing questions without authentication"""
        url = reverse('question-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_question_authenticated(self):
        """Test creating a question when authenticated"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('question-create')
        
        data = {
            'title': "Вопрос о парковке",
            'content': "Есть ли парковка рядом с театром?"
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 3)
        self.assertEqual(Question.objects.latest('created_at').title, "Вопрос о парковке")

    def test_create_question_unauthenticated(self):
        """Test creating a question without authentication should fail"""
        url = reverse('question-create')
        
        data = {
            'title': "Не должен быть создан",
            'content': "Этот вопрос не должен быть создан."
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Question.objects.count(), 2)

    def test_question_detail(self):
        """Test viewing question detail"""
        url = reverse('question-detail', kwargs={'pk': self.question1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Вопрос о возврате билетов")
        self.assertEqual(response.data['is_answered'], False)

    def test_question_with_answer(self):
        """Test viewing question with its answer"""
        url = reverse('question-detail', kwargs={'pk': self.question2.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Вопрос о скидках")
        self.assertEqual(response.data['is_answered'], True)
        self.assertEqual(len(response.data['answers']), 1)
        self.assertEqual(
            response.data['answers'][0]['content'], 
            "Да, студентам предоставляется скидка 20% при предъявлении студенческого билета."
        )


class AnswerAPITest(APITestCase):
    """Тесты API для ответов"""
    
    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='regularpass123'
        )
        
        cls.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        # Create question
        cls.question = Question.objects.create(
            user=cls.regular_user,
            title="Вопрос о расписании",
            content="Где можно найти полное расписание спектаклей на месяц вперед?",
            is_answered=False
        )

    def setUp(self):
        self.client = APIClient()

    def test_create_answer_by_admin(self):
        """Test creating an answer by admin user"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('answer-create', kwargs={'question_id': self.question.pk})
        
        data = {
            'content': "Полное расписание на месяц вперед доступно на главной странице сайта в разделе 'Афиша'."
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.question.refresh_from_db()
        self.assertTrue(self.question.is_answered)
        self.assertEqual(Answer.objects.count(), 1)

    def test_create_answer_by_regular_user_should_fail(self):
        """Test creating an answer by regular user should fail"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('answer-create', kwargs={'question_id': self.question.pk})
        
        data = {
            'content': "Этот ответ не должен быть создан, так как я не администратор."
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.question.refresh_from_db()
        self.assertFalse(self.question.is_answered)
        self.assertEqual(Answer.objects.count(), 0)

    def test_list_answers_for_question(self):
        """Test listing answers for a question"""
        # Create answer first
        answer = Answer.objects.create(
            question=self.question,
            user=self.admin_user,
            content="Ответ на вопрос о расписании."
        )
        
        url = reverse('answer-list', kwargs={'question_id': self.question.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], "Ответ на вопрос о расписании.")
        self.assertEqual(response.data[0]['user'], self.admin_user.username)
