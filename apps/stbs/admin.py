from typing import Any
from django.contrib import admin
from apps.stbs.models import Language, STBManufacture, Natco,  NactoManufactureLanguage, STBNode, STBRelease
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.


class NatcoManufactureAdmin(SimpleHistoryAdmin):

    list_display = ['natco', 'device_name', 'language_name']
    list_editable = ['device_name', 'language_name']


admin.site.register(Language, SimpleHistoryAdmin)
admin.site.register(STBManufacture, SimpleHistoryAdmin)
admin.site.register(NactoManufactureLanguage, NatcoManufactureAdmin)
admin.site.register(Natco, SimpleHistoryAdmin)
admin.site.register(STBNode)
admin.site.register(STBRelease)
