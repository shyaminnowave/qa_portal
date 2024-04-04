import re

from rest_framework import serializers
from apps.testcase_app.models import TestCaseModel, TestCaseStep


class TestCaseSerializerList(serializers.ModelSerializer):

    class Meta:
        fields = ('jira_id', 'test_name', 'jira_summary', 'test_description',
                  'status', 'automation_status')
        model = TestCaseModel

    def to_representation(self, instance):
        represent = super(TestCaseSerializerList, self).to_representation(instance)
        return represent


class TestStepSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TestCaseStep
        fields = ('testcase', 'step_id', 'step_data', 'step_description', 'excepted_result')


class TestCaseSerializer(serializers.ModelSerializer):

    test_steps = TestStepSerializer(many=True, required=False)

    class Meta:
        model = TestCaseModel
        fields = ('test_name', 'jira_id', 'jira_summary', 'test_description', 'comments', 'defects', 'status',
                  'automation_status', 'script_name', 'script', 'test_steps', )

    def validate_test_name(self, value):
        if value is None:
            raise serializers.ValidationError("Test Name Cannot be Empty")
        if value and not re.match(r"^[a-zA-Z\S]+$", value):
            raise serializers.ValidationError("Test Name Cannot Contains Numbers")
        return value


class ExcelSerializer(serializers.Serializer):

    file = serializers.FileField()