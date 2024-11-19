from rest_framework import serializers

from apps.core.models import Projects, ProjectIntegration


class ProjectSerializer(serializers.ModelSerializer):

    logo = serializers.FileField(required=False)

    class Meta:
        model = Projects
        fields = ('id', 'name', 'description', 'logo', 'account')

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