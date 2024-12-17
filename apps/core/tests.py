from django.test import TestCase
from apps.core.models import Project

# Create your tests here.

class TestProjects(TestCase):

    def setUp(self):
        Project.objects.create(
            name='Test Project',
            description='Test Project',
        )

    def test_get_project(self):
        project = Project.objects.get(pk=1)
        self.assertEqual(project.name, 'Test Project')