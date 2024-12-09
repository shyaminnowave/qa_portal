from rest_framework import serializers
from apps.core.models import Project, ProjectIntegration
from analytiqa.helpers.exceptions import QAException
from apps.account.models import Account

class ProjectSerializer(serializers.ModelSerializer):

    name = serializers.CharField(required=True, max_length=100)
    logo = serializers.FileField(required=False)

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'logo', 'account')

    def validate(self, data):
        name = data['name']
        if Project.objects.filter(name=name).exists():
            raise QAException("Project name already exists")
        return data

    def to_representation(self, instance):
        response = super().to_representation(instance)
        integration = instance.integrations.first()
        response['account'] = instance.account.fullname
        response['key'] = integration.key if integration else None
        return response


class ProjectIntegrationSerializer(serializers.ModelSerializer):

    key = serializers.CharField(required=False)

    class Meta:
        model = ProjectIntegration
        fields = ('id', 'key', 'project', 'integration_type', 'domain_url', 'username', 'token')