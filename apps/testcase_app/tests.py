import pytest
from django.test import TestCase
from apps.testcase_app.models import TestCaseModel, NatcoStatus
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
# Create your tests here.


@pytest.mark.django_db
class TestTestCaseModel:

    def test_create_test_case(self):
        test_case = TestCaseModel.objects.create(
            jira_id=1,
            test_name="Test Case 1",
            jira_summary="Summary",
            test_description="Description",
            status=TestCaseModel.ONGOING,
            automation_status=TestCaseModel.IN_DEVELOPMENT,
            script_name="TestScript",
            script="ScriptContent"
        )

        assert test_case.jira_id == 1
        assert test_case.test_name == "Test Case 1"
        assert test_case.jira_summary == "Summary"
        assert test_case.test_description == "Description"
        assert test_case.status == TestCaseModel.ONGOING
        assert test_case.automation_status == TestCaseModel.IN_DEVELOPMENT
        assert test_case.script_name == "TestScript"
        assert test_case.script == "ScriptContent"

    def test_default_values(self):
        test_case = TestCaseModel.objects.create(
            jira_id=2,
            test_name="Test Case 2",
            jira_summary="Summary 2",
            test_description="Description 2",
            automation_status=TestCaseModel.NOT_AUTOMATABLE
        )
        assert test_case.status == TestCaseModel.ONGOING  # default value
        assert test_case.script_name == None  # default value
        assert test_case.script == None  # default value


@pytest.mark.django_db
class TestNatcoList:

    def setup_method(self):
        self.client = APIClient()
        self.test_case = TestCaseModel.objects.create(
            jira_id=1,
            test_name="Test Case 1",
            jira_summary="Summary",
            test_description="Description",
            status=TestCaseModel.ONGOING,
            automation_status=TestCaseModel.IN_DEVELOPMENT,
            script_name="TestScript",
            script="ScriptContent"
        )
        self._url = reverse('testcase-natco', kwargs={'jira_id': self.test_case.jira_id})
        self.response = self.client.get(self._url)

    def test_view_data(self):
        assert self.response.status_code == 200
        response_data = self.response.json()
        assert response_data['count'] == 14


