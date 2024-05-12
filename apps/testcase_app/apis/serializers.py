import re

from rest_framework import serializers
from apps.testcase_app.models import TestCaseModel, TestCaseStep, NatcoStatus
from apps.stbs.apis.serializers import NactoSerializer

class TestCaseSerializerList(serializers.ModelSerializer):

    class Meta:
        model = TestCaseModel
        fields = ('jira_id', 'test_name', 'test_description', 'testcase_type', 'jira_summary',
                  'status', 'automation_status')


class TestCaseStatusUpdateSerializer(serializers.Serializer):

    jira_id = serializers.ListField(child=serializers.IntegerField())
    status = serializers.CharField(required=True)

    def update(self, validated_data, instance=None):
        _testcase = [TestCaseModel.objects.get(jira_id=test_case) for test_case in validated_data.get('jira_id')]
        _status = validated_data.get('status', None)
        for _test in _testcase:
            _test.status = _status
        TestCaseModel.objects.bulk_update(_testcase, fields=['status'])
        return instance


class TestStepSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TestCaseStep
        fields = ('testcase', 'step_id', 'step_data', 'step_description', 'excepted_result')


class NatcoStatusSerializer(serializers.ModelSerializer):

    jira_id = serializers.IntegerField(read_only=True)
    jira_summary = serializers.CharField(read_only=True)

    class Meta:
        model = NatcoStatus
        fields = ('id', 'natco', 'language', 'jira_id', 'jira_summary', 'device', 'test_case', 'status', 'applicable')

    def to_representation(self, instance):
        represent = super(NatcoStatusSerializer, self).to_representation(instance)
        represent['natco'] = instance.natco.natco
        represent['language'] = instance.language.language_name
        represent['device'] = instance.device.name
        represent['test_case'] = instance.test_case.test_name
        represent['jira_id'] = instance.test_case.jira_id
        represent['jira_summary'] = instance.test_case.jira_summary
        represent['applicable'] = "True" if instance.applicable else "False"
        return represent


class TestCaseSerializer(serializers.ModelSerializer):

    test_steps = TestStepSerializer(many=True, required=False)

    class Meta:
        model = TestCaseModel
        fields = ('test_name', 'jira_id', 'jira_summary', 'test_description', 'comments', 'defects', 'status',
                  'automation_status', 'script_name', 'script', 'test_steps')
        

    def validate_test_name(self, value):
        if value is None:
            raise serializers.ValidationError("Test Name Cannot be Empty")
        if value and not re.match(r"^[a-zA-Z\S]+$", value):
            raise serializers.ValidationError("Test Name Cannot Contains Numbers")
        return value


class ExcelSerializer(serializers.Serializer):

    file = serializers.FileField()
