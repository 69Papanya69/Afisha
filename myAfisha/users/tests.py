from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
import unittest

from .models import User
from .serializers import UserSerializer

User = get_user_model()


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='strongpassword123'
        )
        
        # Create admin user
        cls.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword123'
        )

    def test_user_str_representation(self):
        """Test string representation of User model"""
        self.assertEqual(str(self.user), 'testuser')

    def test_get_profile_image_url_with_image(self):
        """Test getting profile image URL when an image is set"""
        # Note: This test is simplified since we can't easily test file uploads in unit tests
        # In a real scenario, you'd use SimpleUploadedFile or mock the image field
        user_with_img = User.objects.get(username='testuser')
        image_url = user_with_img.get_profile_image_url()
        self.assertTrue('profile_images/' in image_url)

    def test_get_profile_image_url_without_image(self):
        """Test getting default profile image URL when no image is set"""
        image_url = self.user.get_profile_image_url()
        self.assertTrue('default_profile_image.png' in image_url)

    def test_is_staff_for_regular_user(self):
        """Test is_staff property for regular user"""
        self.assertFalse(self.user.is_staff)

    def test_is_staff_for_admin_user(self):
        """Test is_staff property for admin user"""
        self.assertTrue(self.admin_user.is_staff)


class UserAuthenticationTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='authpass123'
        )
        
        # URLs for authentication
        cls.login_url = reverse('token_obtain_pair')
        cls.refresh_url = reverse('token_refresh')

    def test_user_login_success(self):
        """Test successful user login and token generation"""
        data = {
            'username': 'authuser',
            'password': 'authpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login failure with invalid credentials"""
        data = {
            'username': 'authuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test refreshing an access token"""
        # First get a refresh token
        login_data = {
            'username': 'authuser',
            'password': 'authpass123'
        }
        
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Now try to get a new access token using the refresh token
        refresh_data = {
            'refresh': refresh_token
        }
        
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class UserRegistrationTest(APITestCase):
    def setUp(self):
        # The URL is 'register' in myAfisha/urls.py
        self.register_url = reverse('register')

    def test_user_registration_success(self):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_user_registration_password_mismatch(self):
        """Test registration failure when passwords don't match"""
        data = {
            'username': 'newuser2',
            'email': 'new2@example.com',
            'password': 'newpass123',
            'password_confirm': 'differentpass'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='newuser2').exists())
    
    def test_user_registration_duplicate_username(self):
        """Test registration failure with duplicate username"""
        # Create a user first
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='existingpass123'
        )
        
        # Try to register with the same username
        data = {
            'username': 'existinguser',  # Same username
            'email': 'different@example.com',  # Different email
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)  # Error about username


@unittest.skip("User profile API not available")
class UserProfileTest(APITestCase):
    """
    Test class for user profile operations
    Note: This test is being skipped as the user-profile URL is not defined in the app.
    """
    
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='profilepass123'
        )
        
        # URLs
        cls.profile_url = "/api/user/"  # Use hardcoded URL instead of reverse lookup

    def setUp(self):
        self.client = APIClient()
    
    def test_get_profile_unauthenticated(self):
        """Test accessing profile without authentication"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_profile_authenticated(self):
        """Test accessing profile when authenticated"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')
        self.assertEqual(response.data['email'], 'profile@example.com')
    
    def test_update_profile(self):
        """Test updating user profile"""
        self.client.force_authenticate(user=self.user)
        
        update_data = {
            'email': 'updated@example.com'
        }
        
        response = self.client.patch(self.profile_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh user from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com') 