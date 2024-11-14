from django.contrib import admin
from apps.testcases.models import TestCaseModel, TestCaseStep, NatcoStatus, TestcaseExcelResult, TestReport, \
                                TestCaseScript, Comment, ScriptIssue
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ExportMixin, ImportExportModelAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
# Register your models here.


class ExportAdmin(ExportMixin, admin.ModelAdmin):
    pass


class TestStepAdmin(admin.TabularInline):

    extra = 3
    model = TestCaseStep


class CommentAdmin(GenericTabularInline):

    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    model = Comment


class TestCaseModelAdmin(SimpleHistoryAdmin, ExportAdmin):

    list_display = ['id', 'test_name', 'priority', 'testcase_type', 'automation_status']
    # search_fields = ('jira_id',)
    list_filter = ('priority', 'testcase_type')
    list_editable = ('test_name', 'priority', 'testcase_type', 'automation_status')
    inlines = [TestStepAdmin, CommentAdmin]


class NatcoStatusAdmin(SimpleHistoryAdmin):

    list_display = ['test_case', 'language', 'device', 'status']


class TestResultAdmin(admin.ModelAdmin):

    list_display = ['id', 'testcase', 'natco']
    search_fields = ('testcase',)
    list_filter = ['node_id', 'natco', 'stb_release', 'stb_firmware', 'stb_android', 'stb_build']


class ReportAdmin(admin.ModelAdmin):

    list_display = ['job_id', 'testcase', 'node']
    list_filter = ['node']


@admin.register(ScriptIssue)
class ScriptIssueAdmin(SimpleHistoryAdmin):

    list_display = ['id', 'summary']
    inlines = [CommentAdmin]

admin.site.register(TestCaseModel, TestCaseModelAdmin)
admin.site.register(TestcaseExcelResult, TestResultAdmin)
admin.site.register(NatcoStatus, NatcoStatusAdmin)
admin.site.register(TestReport, ReportAdmin)
admin.site.register(TestCaseScript)
admin.site.register(Comment)
admin.site.register(TestCaseStep, ImportExportModelAdmin)

# admin.site.register(Comment)