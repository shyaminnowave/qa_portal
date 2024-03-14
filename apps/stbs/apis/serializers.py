from rest_framework import serializers
from apps.stbs.models import Language
import re


class LanguageSerializer(serializers.Serializer):

    language_name = serializers.CharField(required=True, max_length=20)

    def validate_language(self, value):
        if value is None:
            raise serializers.ValidationError("Language Field cannot be Empty")
        elif value and not re.match(r"^[a-zA-Z\S]+$", value):
            raise serializers.ValidationError("Language Cannot Contain Numbers and Symbols")
        return value

    def create(self, validated_data):
        return Language.objects.create(language_name=validated_data.get('language'))
    
    def update(self, instance, validated_data):
        instance.language_name = validated_data.get('language', instance.language)
        instance.save()
        return instance
