from django.contrib import admin
from apps.testcase_app.models import TestCaseModel, TestCaseStep, NatcoStatus
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.


class TestStepAdmin(admin.TabularInline):

    extra = 3
    model = TestCaseStep


class TestCaseModelAdmin(SimpleHistoryAdmin):

    inlines = [TestStepAdmin]


class NatcoStatusAdmin(SimpleHistoryAdmin):

    list_display = ['test_case', 'language', 'device', 'status']


admin.site.register(TestCaseModel, TestCaseModelAdmin)
admin.site.register(NatcoStatus, NatcoStatusAdmin)
