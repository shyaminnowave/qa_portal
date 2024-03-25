from typing import Any
from django.contrib import admin
from apps.stbs.models import Language, STBManufacture, Natco,  NactoManufactureLanguage
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.

admin.site.register(Language, SimpleHistoryAdmin)
admin.site.register(STBManufacture, SimpleHistoryAdmin)
admin.site.register(NactoManufactureLanguage, SimpleHistoryAdmin)
admin.site.register(Natco, SimpleHistoryAdmin)
