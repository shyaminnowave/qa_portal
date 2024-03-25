import pytest
from django.test import TestCase
from apps.testcase_app.models import  TestCaseModel

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
            automation_status=TestCaseModel.INDEVELOPMENT,
            script_name="TestScript",
            script="ScriptContent"
        )

        assert test_case.jira_id == 1
        assert test_case.test_name == "Test Case 1"
        assert test_case.jira_summary == "Summary"
        assert test_case.test_description == "Description"
        assert test_case.status == TestCaseModel.ONGOING
        assert test_case.automation_status == TestCaseModel.INDEVELOPMENT
        assert test_case.script_name == "TestScript"
        assert test_case.script == "ScriptContent"

    def test_default_values(self):
        test_case = TestCaseModel.objects.create(
            jira_id=2,
            test_name="Test Case 2",
            jira_summary="Summary 2",
            test_description="Description 2",
            automation_status=TestCaseModel.NOTAUTOMATABLE
        )
        assert test_case.status == TestCaseModel.ONGOING  # default value
        assert test_case.script_name == "Tets"  # default value
        assert test_case.script == "Tets"  # default value
