from typing import Any
from django.test import TestCase
from django.contrib.auth import get_user_model
from pkg_resources import DistributionNotFound, get_distribution
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import Group
# Create your tests here.

User = get_user_model()

class UserCreationTestCase(TestCase):

    def setUp(self) -> None:
        User.objects.Create(email="shyam6132@gmail.com", password="shyam", fullname='shyam')

    def test_get_user(self):
        user = User.objects.get(email="shyam6132@gmail.com")
        self.assertEqual(user.email, "shyam6132@gmail.com")
