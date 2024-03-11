from typing import Any
from django.contrib import admin
from apps.account.models import Account
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class AccountAdmin(UserAdmin):
    readonly_fields = ['password']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['is_superuser', 'is_staff'].disabled = True
        return form

admin.site.register(Account, AccountAdmin)