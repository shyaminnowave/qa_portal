from django.contrib import admin
from apps.core.models import Project, ProjectIntegration

# Register your models here.

class ProjectIntegrationAdmin(admin.ModelAdmin):

    list_display = ['id', 'key']

admin.site.register(Project)
admin.site.register(ProjectIntegration, ProjectIntegrationAdmin)