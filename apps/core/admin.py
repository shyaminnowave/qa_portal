from django.contrib import admin
from apps.core.models import Projects, ProjectIntegration

# Register your models here.

class ProjectIntegrationAdmin(admin.ModelAdmin):

    list_display = ['id', 'key']

admin.site.register(Projects)
admin.site.register(ProjectIntegration, ProjectIntegrationAdmin)