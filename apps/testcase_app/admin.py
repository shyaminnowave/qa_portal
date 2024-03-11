from django.contrib import admin
from apps.testcase_app.models import TestCaseModel, TestCaseStep

# Register your models here.

class TestStepAdmin(admin.TabularInline):

    model = TestCaseStep


class TestCaseModelAdmin(admin.ModelAdmin):

    inlines = [TestStepAdmin]

admin.site.register(TestCaseModel, TestCaseModelAdmin)
