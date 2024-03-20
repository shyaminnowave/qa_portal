from rest_framework import serializers
from apps.testcase_app.models import TestCaseModel, TestCaseStep


class TestCaseSerializerList(serializers.Serializer):
    
    
    TODO = 'todo'
    ONGOING = 'ongoing'
    COMPLETED = 'completed'

    STATUS_CHOICES = (
        (TODO, 'Todo'),
        (ONGOING, 'On-Going'),
        (COMPLETED, 'Completed')
    )

    test_name = serializers.CharField()
    jira_id = serializers.IntegerField()
    jira_summary = serializers.CharField()
    test_description = serializers.CharField()
    status = serializers.ChoiceField(choices=STATUS_CHOICES)


class TestStepSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TestCaseStep
        fields = ('testcase', 'step_id', 'step_data', 'step_description')


class TestCaseSerializer(serializers.ModelSerializer):

    test_steps = TestStepSerializer(many=True, required=False)
    
    class Meta:
        model = TestCaseModel
        fields = ('test_name', 'jira_id', 'jira_summary', 'test_description', 'comments', 'defects', 'status', 'script_name', 'script', 'test_steps', )

