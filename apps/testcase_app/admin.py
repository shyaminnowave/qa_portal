from django.contrib import admin
from apps.testcase_app.models import TestCaseModel, TestCaseStep
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.

class TestStepAdmin(admin.TabularInline):

    model = TestCaseStep


class TestCaseModelAdmin(SimpleHistoryAdmin):

    inlines = [TestStepAdmin]

admin.site.register(TestCaseModel, TestCaseModelAdmin)
