from typing import Any
from django.test import TestCase
import pytest
from django.contrib.auth import get_user_model
from pkg_resources import DistributionNotFound, get_distribution
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
# Create your tests here.

User = get_user_model()

class TestUser(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.assertEqual(admin_user.username, 'admin')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class TestLoginView(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test1@gmail.com',
            'first_name': 'shyam',
            'last_name': 'kumar',
            'password': 'shyamkumar',
            'confirm_password': 'shyamkumar'
        }
        self.url = reverse('create-user')
    
    def test_create_user(self):
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):
        user = User.objects.create_user(email='tets@gmail.com',
                                        username='test',
                                        password='shyamkumar')
        self.data = {
            'email': 'tets@gmail.com',
            'password': 'shyamkumar'
        }
        self._url = reverse('login')
        response = self.client.post(self._url, self.data)
        self.assertContains(response, 'access', status_code=status.HTTP_200_OK)

    def test_wrong_user(self):
        user = User.objects.create_user(email='tets@gmail.com',
                                        username='test',
                                        password='shyamkumar')
        
        self._url = reverse('login')
        self.data = {
            'email': 'tets@gmail.com',
            'password': 'shyamumar'
        }
        response = self.client.post(self._url, self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)