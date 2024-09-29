from django.contrib import admin
from ..stb_tester.models import StbConfiguration, StbResult
from solo.admin import SingletonModelAdmin
# Register your models here.


class StbResultAdmin(admin.ModelAdmin):

    list_display = ['result_id', 'testcase']
    list_filter = ['testcase']

admin.site.register(StbConfiguration)
admin.site.register(StbResult, StbResultAdmin)
