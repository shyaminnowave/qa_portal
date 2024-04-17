from django.test import TestCase
import pytest
from pkg_resources import DistributionNotFound, get_distribution
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from apps.stbs.models import Language
from django.core.exceptions import ValidationError
from apps.stbs.models import STBManufacture, Language, NactoManufactureLanguage, Natco
from apps.stbs.apis.serializers import LanguageSerializer, STBManufactureSerializer
# Create your tests here.


class TestLanguageModel(TestCase):

    def setUp(self):
        Language.objects.create(language_name="Python")
        Language.objects.create(language_name="JavaScript")

    def test_language_str(self):
        python = Language.objects.get(language_name="Python")
        javascript = Language.objects.get(language_name="JavaScript")
        self.assertEqual(str(python), "Python")
        self.assertEqual(str(javascript), "JavaScript")


class TestLanguageSerializer(TestCase):
    def setUp(self):
        self.data = {
            "language_name": "Python"
        }

    def test_language_create(self):
        serializer = LanguageSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_language(self):
        invalid_data = {
            'language_name': "223payr"
        }
        serializer = LanguageSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_language(self):
        language = Language.objects.create(language_name="Test")
        serializer = LanguageSerializer(language)
        self.assertEqual(serializer.data['language_name'], 'Test')   


class TestSTBManufacture(TestCase):

    def setUp(self) -> None:
        STBManufacture.objects.create(name="Python")
        STBManufacture.objects.create(name="JavaScript")
        self.data = {
            "name": "Python"
        }

    def test_stb(self):
        stb = STBManufacture.objects.get(name="Python")
        self.assertEqual(stb.name, 'Python')

    def test_stb_create(self):
        self._data = {
            "name": "Java"
        }
        serializer = STBManufactureSerializer(data=self._data)
        self.assertTrue(serializer.is_valid())
        print(serializer.errors)

    def test_invalid_stb(self):
        invalid_data = {
            'name': "223payr"
        }
        serializer = STBManufactureSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_stb_serializer(self):
        language = STBManufacture.objects.create(name="Test")
        serializer = STBManufactureSerializer(language)
        self.assertEqual(serializer.data['name'], 'Test') 
    