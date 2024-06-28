import re
from rest_framework import serializers
from apps.testcase_app.models import TestCaseModel, TestCaseStep, NatcoStatus, TestResult
from apps.stbs.models import Natco, NactoManufactureLanguage
from collections import defaultdict
from apps.stbs.apis.serializers import NactoSerializer


class TestCaseSerializerList(serializers.ModelSerializer):

    class Meta:
        model = TestCaseModel
        fields = ('get_jira_id', 'test_name', 'priority', 'testcase_type',
                  'status', 'automation_status')


class BulkFieldUpdateSerializer(serializers.Serializer):

    id_fields = serializers.ListField(child=serializers.IntegerField())
    field = serializers.CharField()

    def update_testcase_status(self, validated_data, instance=None):
        _testcase = [TestCaseModel.objects.get(jira_id=test_case) for test_case in validated_data.get('id_fields')]
        _status = validated_data.get('field', None)
        for _test in _testcase:
            _test.status = _status
        instance = TestCaseModel.objects.bulk_update(_testcase, fields=['status'])
        return True if instance else False

    def update_testcase_automation(self, validated_data, instance=None):
        _testcase = [TestCaseModel.objects.get(jira_id=test_case) for test_case in validated_data.get('id_fields')]
        _status = validated_data.get('field', None)
        for _test in _testcase:
            _test.automation_status = _status
        instance = TestCaseModel.objects.bulk_update(_testcase, fields=['automation_status'])
        return True if instance else False

    def update_natco_status(self, validated_data, instance=None):
        _natcos = [NatcoStatus.objects.get(id=i) for i in validated_data.get('id_fields')]
        print(_natcos)
        _status = validated_data.get('field', None)
        for _natco in _natcos:
            _natco.status = _status
        instance = NatcoStatus.objects.bulk_update(_natcos, fields=['status'])
        return True if instance else False


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


class NavbarFilterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Natco
        fields = ('natco', 'manufacture')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        natco = rep.pop('natco')
        rep['manufacture'] = [i.name for i in instance.manufacture.all()]
        return {natco: {'device': rep['manufacture']}}


class NatcoGraphAPISerializer(serializers.Serializer):
    natco = serializers.CharField(max_length=200, required=True)
    avg_load_time = serializers.DecimalField(max_digits=5, decimal_places=4, required=False)
    avg_cpu_load = serializers.DecimalField(max_digits=5, decimal_places=4, required=False)
    avg_ram_load = serializers.DecimalField(max_digits=5, decimal_places=4, required=False)

    def __init__(self, *args, **kwargs):
        request = kwargs['context']['request'] if 'context' in kwargs and 'request' in kwargs['context'] else None
        if request:
            if request.path.split('/')[-2] == 'load_time':
                self.fields = {
                    'natco': self.fields['natco'],
                    'avg_load_time': self.fields['avg_load_time']
                }
            elif request.path.split('/')[-2] == 'cpu_load':
                self.fields = {
                    'natco': self.fields['natco'],
                    'avg_cpu_load': self.fields['avg_cpu_load']
                }
            elif request.path.split('/')[-2] == 'ram_load':
                self.fields = {
                    'natco': self.fields['natco'],
                    'avg_ram_load': self.fields['avg_ram_load']
                }
        super().__init__(*args, **kwargs)


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