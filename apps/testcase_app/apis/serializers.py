import re
from rest_framework import serializers
from apps.testcase_app.models import TestCaseModel, TestCaseStep, NatcoStatus, TestResult
from apps.stbs.apis.serializers import NactoSerializer


class TestCaseSerializerList(serializers.ModelSerializer):

    class Meta:
        model = TestCaseModel
        fields = ('get_jira_id', 'test_name', 'priority', 'testcase_type',
                  'status', 'automation_status')


class BulkFieldUpdateSerializer(serializers.Serializer):

    @staticmethod
    def get_corresponding_query(cls, _field, validated_data):
        _querysets = {
            'automation_status': [cls.objects.get(jira_id=i) for i in validated_data.get('id_fields')],
            'test_status': [cls.objects.get(jira_id=i) for i in validated_data.get('id_fields')],
            # 'natco_status': [cls.objects.get(id=i) for i in validated_data.get('id_fields')]
        }
        if _field in _querysets:
            print('hello')
            return _field, _querysets[_field]
        else:
            raise KeyError(f"Field {_field} not found in querysets")

    id_fields = serializers.ListField(child=serializers.IntegerField())
    field = serializers.CharField()

    def update(self, validated_data, instance=None):
        cls = self.context.get('class')
        _field = self.context.get('field')
        key, _instance = self.get_corresponding_query(cls, _field, validated_data)
        print(_field, _instance)
        _status = validated_data.get('field', None)
        for _inst in _instance:
            _inst.field = _status
        if key == 'automation_status':
            print(key)
            cls.objects.bulk_update(_instance, fields=['automation_status'])
        elif _field == 'test_status':
            cls.objects.bulk_update(_instance, fields=['status'])
        return instance


class TestCaseAutomationStatusUpdateSerializer(serializers.Serializer):

    jira_id = serializers.ListField(child=serializers.IntegerField())
    automation_status = serializers.CharField(required=True)

    def update(self, validated_data, instance=None):
        _testcase = [TestCaseModel.objects.get(jira_id=test_case) for test_case in validated_data.get('jira_id')]
        _status = validated_data.get('automation_status', None)
        print(_status)
        for _test in _testcase:
            _test.automation_status = _status
        TestCaseModel.objects.bulk_update(_testcase, fields=['automation_status'])
        return instance


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
        fields = ('testcase', 'step_id', 'step_data', 'step_action', 'excepted_result')


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
    

class TestResultDRPSerializer(serializers.Serializer):

    node_id = serializers.CharField(max_length=255)


class ExcelSerializer(serializers.Serializer):

    file = serializers.FileField()


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = '__all__'


class DistinctTestResultSerializer(serializers.Serializer):
    testcase = serializers.CharField()
    natco = serializers.CharField()
    cpu_usage = serializers.CharField()
    ram_usage = serializers.CharField()
    load_time = serializers.CharField()

    def get_min_cpu(self, obj):
        return obj['min_cpu']

    def get_min_ram(self, obj):
        return obj['min_ram']