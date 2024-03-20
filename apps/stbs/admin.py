from typing import Any
from django.contrib import admin
from apps.stbs.models import Language, STBManufacture, Natco,  NactoManufactureLanguage
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
# Register your models here.

class LanguageAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.request_method = 'PUT' if change else 'POST'
        obj.history_user = request.user
        super().save_model(request, obj, form, change)

    def log_change(self, request, object, message):
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(object).pk,
            object_id=object.id,
            object_repr=str(object),
            action_flag=CHANGE,
            change_message=message
        )

admin.site.register(Language, LanguageAdmin)
admin.site.register(STBManufacture)
admin.site.register(NactoManufactureLanguage)
admin.site.register(Natco)
