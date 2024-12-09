
from rest_framework import serializers
from simple_history.utils import update_change_reason
from decimal import Decimal
from apps.account.models import Account
from apps.testcases.models import TestCaseModel, TestCaseStep, NatcoStatus, TestcaseExcelResult, TestReport, \
    TestCaseChoices, Comment, ScriptIssue, TestCaseScript, TestCaseMetaData
from apps.stbs.models import Natco, NactoManufacturesLanguage, NatcoRelease
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from apps.stb_tester.serializers import ResultSerializer
from django.shortcuts import get_object_or_404
# from apps.stb_tester.views import BaseAPI
from collections import defaultdict
from apps.stbs.apis.serializers import NactoSerializer


class TestCaseSerializerList(serializers.ModelSerializer):
    twenty_result = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TestCaseModel
        fields = ('id', 'test_name', 'priority', 'testcase_type',
                  'status', 'automation_status', 'twenty_result')

    def get_twenty_result(self, obj):
        last_twenty_results = obj.testcase_result.order_by('-start_time')[:20]
        return [result.result for result in last_twenty_results]


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


class StepDataSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    step_number = serializers.IntegerField(min_value=1, max_value=100)
    step_action = serializers.CharField()
    step_data = serializers.CharField()
    expected_result = serializers.CharField()


class TestStepSerializer(serializers.Serializer):

    testcase = serializers.PrimaryKeyRelatedField(queryset=TestCaseModel.objects.all(), allow_null=True, required=False)
    step_number = serializers.IntegerField(min_value=1)
    step_action = serializers.CharField(required=False)
    step_data = serializers.CharField(required=False)
    expected_result = serializers.CharField(required=False)

    def create(self, validated_data):
        if validated_data:
            teststep = TestCaseStep.objects.create(testcase=validated_data.get('testcase'), step_number=validated_data.get('step_number'),
                                                   step_action=validated_data.get('step_action'),
                                                   step_data=validated_data.get('step_data', None),
                                                   expected_result=validated_data.get('expected_result'))
            return teststep
        return False

    def update(self, instance, validated_data):
        if instance:
            instance.step_action = validated_data.get('step_action')
            instance.step_data = validated_data.get(
                'step_data', None
            )
            instance.expected_result = validated_data.get('expected_result')
        instance.save()
        return instance

    def delete(self, instance):
        step_number_to_remove = instance.step_number
        testcase = instance.testcase
        instance.delete()
        try:
            remaining_steps = TestCaseStep.objects.filter(testcase=testcase, step_number__gt=step_number_to_remove)
            for step in remaining_steps:
                step.step_number -= 1
                step.save()
            return instance
        except TestCaseStep.DoesNotExists:
            return False


class NatcoStatusSerializer(serializers.ModelSerializer):

    jira_id = serializers.IntegerField(read_only=True)
    summary = serializers.CharField(read_only=True)
    history_change_reason = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = NatcoStatus
        fields = ['id', 'natco', 'language', 'jira_id', 'summary', 'device', 'test_case', 'status', 'applicable',
                  'modified', 'history_change_reason']


    def __init__(self, *args, **kwargs):
        request = kwargs['context']['request'] if 'context' in kwargs and 'request' in kwargs['context'] else None
        resolve_match = getattr(request, 'resolver_match', None)
        if resolve_match.url_name == 'natco-details':
            fields = ['user', 'modified']
            self.Meta.fields.extend(fields)
        if resolve_match.url_name == 'testcase-natco':
            self.Meta.fields = ['id', 'natco', 'language', 'jira_id', 'summary', 'device', 'status',
                                'applicable', 'history_change_reason', 'modified']
        super(NatcoStatusSerializer, self).__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        history_change_reason = validated_data.get('history_change_reason', 'Natco Status Changed')
        instance = super().update(instance, validated_data)
        if history_change_reason:
            update_change_reason(instance, history_change_reason)
        return instance

    def to_representation(self, instance):
        represent = super(NatcoStatusSerializer, self).to_representation(instance)
        represent['test_case'] = instance.test_case.test_name
        represent['jira_id'] = instance.test_case.jira_id
        represent['summary'] = instance.test_case.summary if instance.test_case.summary else None
        represent['modified'] = instance.modified.fullname if instance.modified else None
        represent['applicable'] = "True" if instance.applicable else "False"
        return represent


class TestCaseSerializer(serializers.ModelSerializer):

    test_steps = StepDataSerializer(many=True, required=False)
    created = serializers.SerializerMethodField(required=False, read_only=True)
    modified = serializers.SerializerMethodField(required=False, read_only=True)
    last_fifty_result = serializers.SerializerMethodField(required=False, read_only=True)
    history_change_reason = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = TestCaseModel
        fields = ('id', 'test_name', 'jira_id', 'summary', 'description', 'status', 'priority',
                  'automation_status', 'test_steps', 'testcase_type', 'created', 'modified', 'last_fifty_result',
                  'created_by', 'history_change_reason')

    def __init__(self, *args, **kwargs):
        request = kwargs['context']['request'] if 'context' in kwargs and 'request' in kwargs['context'] else None
        resolve_match = getattr(kwargs['context']['request'], 'resolver_match', None)
        if request and request.path == '/api/create/test-case/':
            self.Meta.fields = ('id', 'test_name', 'summary', 'description', 'testcase_type', 'created', 'modified',
                                'status', 'automation_status', 'last_fifty_result', 'test_steps', 'history_change_reason')
        if resolve_match.url_name == 'testcase-details':
            self.Meta.fields = '__all__'
        super().__init__(*args, **kwargs)

    def validate_test_name(self, value):
        if value is None:
            raise serializers.ValidationError("Test Name Cannot be Empty")
        return value

    def get_created(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y")

    def get_modified(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y")

    def get_last_fifty_result(self, obj):
        _data = obj.testcase_result.order_by('-start_time').only('result_url', 'result', 'failure_reason')[:50]
        return [
            {
                "result_id": result.result_id,
                "result": result.result,
                "failure_reason": result.failure_reason
            }
            for result in _data
        ] if _data else []

    def update(self, instance, validated_data):
        message = ''
        if instance.description != validated_data.get("description", instance.description):
            message = 'Description Changed'
        else:
            message = 'Script Issues'
        history_change_reason = validated_data.get('history_change_reason', message)
        instance = super().update(instance, validated_data)
        if history_change_reason:
            update_change_reason(instance, history_change_reason)
        return instance


class TestResultDRPSerializer(serializers.Serializer):

    node_id = serializers.CharField(max_length=255)


class ExcelSerializer(serializers.Serializer):

    file = serializers.FileField()


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestcaseExcelResult
        fields = '__all__'


class NavbarFilterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Natco
        fields = ('natco',)

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     natco = rep.pop('natco')
    #     return natco
        # rep['manufacture'] = [i.name for i in instance.manufacture.all()]
        # return {natco: {'device': rep['manufacture']}}


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


class MetricSerializer(serializers.Serializer):
    natco = serializers.CharField(max_length=10)
    builname = serializers.CharField(max_length=10)
    value = serializers.FloatField()


class ReportSerializer(serializers.ModelSerializer):

    testcase = serializers.CharField(max_length=200, source='testcase__test_name')
    node = serializers.CharField(max_length=200)
    cpu = serializers.CharField(max_length=20)
    loadtime = serializers.CharField(max_length=20)
    ram = serializers.CharField(max_length=20)
    natco = serializers.SerializerMethodField()

    class Meta:
        model = TestReport
        fields = ['testcase', 'node', 'natco', 'cpu', 'loadtime', 'ram']

    def get_natco(self, obj):
        natco_release = NatcoRelease.objects.filter(id=obj['node']).first()
        if natco_release:
            return natco_release.natco()
        return None


class GraphReportSerializer(serializers.Serializer):

    testcase = serializers.CharField(max_length=200, source='testcase__test_name')
    cpu = serializers.CharField(max_length=20)
    loadtime = serializers.CharField(max_length=20)
    ram = serializers.CharField(max_length=20)
    natco = serializers.SerializerMethodField()
    natco_version = serializers.SerializerMethodField()

    class Meta:
        model = TestReport
        fields = ['testcase', 'natco', 'natco_version', 'cpu', 'loadtime', 'ram']

    def get_natco(self, obj):
        natco_release = NatcoRelease.objects.filter(id=obj['node']).first()
        if natco_release:
            return natco_release.natcos.natco
        return None

    def get_natco_version(self, obj):
        natco_release = NatcoRelease.objects.filter(id=obj['node']).first()
        if natco_release:
            return natco_release.natco()
        return None

    # def to_representation(self, instance):
    #     _data = defaultdict(lambda: defaultdict(list))
    #     rep = super().to_representation(instance)
    #     print(rep)
    #     # `instance` is assumed to be a queryset or a list of TestReport instances
    #     for item in rep:
    #         testcase_name = item.get('testcase')  # Accessing related field via ORM
    #         natco, natco_release = self.get_natco(item)
    #         cpu_data = {
    #             'natco': natco,
    #             'buildname': natco_release,
    #             'value': item.get('cpu')
    #         }
    #         ram_data = {
    #             'natco': natco,
    #             'buildname': natco_release,
    #             'value': item.get('cpu')
    #         }
    #         load_data = {
    #             'natco': natco,
    #             'buildname': natco_release,
    #             'value': item.get('cpu')
    #         }
    #         _data[testcase_name]['cpu'].append(cpu_data)
    #         _data[testcase_name]['RAM'].append(ram_data)
    #         _data[testcase_name]['Load'].append(load_data)
    #     final_output = []
    #     for testcase_name, metrics in _data.items():
    #         final_output.append({
    #             'testcaseName': testcase_name,
    #             'cpu': metrics['cpu'],
    #             'RAM': metrics['RAM'],
    #             'Load': metrics['Load']
    #         })
    #     return final_output


class TestCaseFilterSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=20)
    value = serializers.CharField(max_length=20)


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


class HistorySerializer(serializers.Serializer):

    history_id = serializers.PrimaryKeyRelatedField(read_only=True)
    history_type = serializers.CharField()
    history_change_reason = serializers.CharField()
    history_user = serializers.CharField()
    history_date = serializers.DateTimeField()
    changed_to = serializers.SerializerMethodField()
    test_name = serializers.CharField()

    def get_changed_to(self, obj):
        try:
            # Retrieve the TestCaseModel instance by ID
            _instance = TestCaseModel.objects.get(id=obj.id)
            # Fetch all historical records, filtering by type if needed
            history_records = list(_instance.history.filter(history_type='~').order_by('history_date'))

            # Locate the current record's position in the historical timeline
            current_index = history_records.index(obj)
            if current_index == 0:
                return ["Natco status changed"]  # No previous records to compare

            # Compare current record to the previous one
            old_record = history_records[current_index - 1]
            new_record = obj
            delta = new_record.diff_against(old_record)

            # Map changes, verifying data exists for both old and new states
            differences = {
                change.field: f"changed from '{change.old}' to '{change.new}'"
                for change in delta.changes
                if change.old is not None and change.new is not None
            }

            # If no differences are detected, return a message or empty list
            if not differences:
                differences["natco_status"] = "Natco status changed"

            # Format differences as a list of dictionaries
            return [{field: desc} for field, desc in differences.items()]

        except (ValueError, TestCaseModel.DoesNotExist):
            return ["Error retrieving change details"]

    def get_created(self, obj):
        data = datetime.fromisoformat(str(obj))
        return data.strftime("%d-%m-%Y")

    def account_fullname(self, obj):
        if obj:
            _data = Account.objects.get(email=obj)
            return _data.fullname
        return None

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['history_type'] = "Create" if instance.history_type == '+' else "Update" if instance.history_type == '~' else "Delete"
        represent['changed_to'] = self.get_changed_to(instance)
        represent['history_change_reason'] = instance.history_change_reason if instance.history_change_reason else "Natco status changed"
        represent['history_user'] = self.account_fullname(
            instance.history_user
        ) if instance.history_user else None
        represent['history_date'] = self.get_created(instance.history_date)
        return represent


class CommentSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'comments', 'object_id', 'created_by')

    def get_model_instance(self):
        model_instance =  ContentType.objects.get_for_model(ScriptIssue)
        return model_instance

    def get_object_instance(self, id=id):
        instance = get_object_or_404(ScriptIssue, pk=id)
        return instance

    def account_instance(self, obj):
        if obj is not None:
            try:
                instance = Account.objects.get(email=obj)
                return instance.email
            except Account.DoesNotExist:
                return None
        return None

    def create(self, validated_data):
        object_id = validated_data.pop('object_id', None)
        obj_instance = self.get_object_instance(id=object_id)
        if obj_instance:
            cmd = Comment.objects.create(content_type=self.get_model_instance(), object_id=obj_instance.id,
                                         **validated_data)
            return True
        raise ScriptIssue.DoesNotExist("Object Does Not Exist")

    def update(self, instance, validated_data):
        if instance:
            instance.comments = validated_data.get('comments', instance.comments)
            instance.status = validated_data.get('status', instance.status)
            instance.resolved_by = validated_data.get('resolved_by', instance.resolved_by)
            instance.save()
        return instance


class IssueCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'comments', 'created_by']

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['created_by'] = instance.created_by.fullname
        return represent

class ScriptIssueList(serializers.ModelSerializer):

    class Meta:
        model = ScriptIssue
        fields = ('id', 'summary', 'status', 'created_by', 'resolved_by')

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['created_by'] = instance.created_by.fullname if instance.created_by else None
        represent['resolved_by'] = instance.resolved_by.fullname if instance.resolved_by else None
        return represent


class ScriptIssueSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(read_only=True)
    issues_comment = IssueCommentSerializer(many=True, read_only=True, source='comment.all')
    created = serializers.SerializerMethodField()
    modified = serializers.SerializerMethodField()

    class Meta:
        model = ScriptIssue
        fields = ['id', 'script_id', 'summary', 'description', 'status', 'issues_comment', 'created_by', 'resolved_by', 'created',
                  'modified']

    def get_account_instance(self, email):
        if email is not None:
            try:
                instance = Account.objects.get(email=email)
                return instance
            except Account.DoesNotExist:
                return None
        return None

    def get_created(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y")

    def get_modified(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y")

    def create(self, validated_data, id=id):
        if isinstance(id, int):
            __instance = get_object_or_404(TestCaseModel, id=id)
            if __instance:
                resolved = validated_data.pop('resolved_by', None)
                script = ScriptIssue.objects.create(testcase=__instance,
                                                    **validated_data)
                return True
            raise TestCaseModel.DoesNotExist("Testcase Model Does Not Exist")
        raise serializers.ValidationError(f"Expected Integer Id but received {type(id)}")

    def update(self, instance, validated_data):
        if instance:
            instance.summary = validated_data.get('summary', instance.summary)
            instance.status = validated_data.get('status', instance.status)
            instance.resolved_by = self.get_account_instance(validated_data.get('resolved_by', instance.resolved_by))
            instance.description = validated_data.get('description', instance.description)
            instance.save()
        return instance

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['created_by'] = instance.created_by.fullname if instance.created_by else None
        represent['resolved_by'] = instance.resolved_by.fullname if instance.resolved_by else None
        return represent


class TestcaseScriptSerializer(serializers.ModelSerializer):

    scripts = ScriptIssueList(many=True, read_only=True)
    created = serializers.SerializerMethodField(required=False, read_only=True)
    modified = serializers.SerializerMethodField(required=False, read_only=True)

    def validate_natco(self, obj):
        if obj in ['AT', 'PL', 'HR', 'HU', "MKT", "ME"]:
            return obj
        else:
            raise serializers.ValidationError("Natco Does Not Exist")

    class Meta:
        model = TestCaseScript
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        request = kwargs['context']['request'] if 'context' in kwargs and 'request' in kwargs['context'] else None
        resolver_match = getattr(request, 'resolver_match', None)
        if request and resolver_match.url_name == 'testcase-scriptlist':
            self.Meta.fields = (
                'id',
                'script_name', 
                'script_location',
                'scripts',
                'script_type',
                'description',
                'developed_by',
                'modified_by',
                'natco',
                'created',
                'modified',
            )
        elif request and resolver_match.url_name == 'testcase-create-script':
            self.Meta.fields = (
                'id',
                'script_name',
                'script_location',
                'scripts',
                'script_type',
                'testcase',
                'description',
                'developed_by',
                'natco',
                'created',
                'modified'
            )
        super().__init__(*args, **kwargs)


    def get_created(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y")

    def get_modified(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y")

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        resolve_match = getattr(self.context['request'], 'resolver_match', None)
        if resolve_match.url_name == 'testcase-scriptlist':
            represent['developed_by'] = instance.developed_by.fullname if instance.developed_by else None
        else:
            represent['developed_by'] = instance.developed_by.fullname if instance.developed_by else None
            represent['reviewed_by'] = instance.reviewed_by.fullname if instance.reviewed_by else None
            represent['modified_by'] = instance.modified_by.fullname if instance.modified_by else None
        return represent


class TestMetaDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestCaseMetaData
        fields = ('id', 'testcase', 'get_testscore')

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['testcase'] = instance.testcase.test_name
        return represent