from django.contrib import admin
from apps.testcase_app.models import TestCaseModel, TestCaseStep, NatcoStatus, TestResult
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.


class TestStepAdmin(admin.TabularInline):

    extra = 3
    model = TestCaseStep


class TestCaseModelAdmin(SimpleHistoryAdmin):

    list_display = ['jira_id', 'test_name', 'priority', 'testcase_type']
    search_fields = ('jira_id',)
    list_filter = ('priority', 'testcase_type')
    list_editable = ('test_name', 'priority', 'testcase_type')
    inlines = [TestStepAdmin]


class NatcoStatusAdmin(SimpleHistoryAdmin):

    list_display = ['test_case', 'language', 'device', 'status']


class TestResultAdmin(admin.ModelAdmin):

    list_display = ['id', 'testcase']
    list_filter = ['node_id', 'natco', 'stb_release', 'stb_firmware', 'stb_android', 'stb_build']


admin.site.register(TestCaseModel, TestCaseModelAdmin)
admin.site.register(TestResult, TestResultAdmin)
admin.site.register(NatcoStatus, NatcoStatusAdmin)
