from rest_framework import serializers
from apps.account.models import Account
from rest_framework.views import exception_handler
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from apps.account.utils import generate_user
from django.core.exceptions import ValidationError
import re

User = get_user_model()

class CustomValidation(serializers.ValidationError):

    def __init__(self, message):
        super().__init__({'message': message})

class EmailExistValidation(serializers.ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Email Already Exists')
    default_code = 'Already Exists'

    def __init__(self, detail=None, code=None):
        super().__init__(detail, code)


class AccountSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True, max_length=30)
    fullname = serializers.CharField(required=True, max_length=30)
    password = serializers.CharField(required=True, max_length=20)
    confirm_password = serializers.CharField(required=True, max_length=20, write_only=True)
        
    class Meta:
        model = User
        fields = ('email', 'fullname', 'password', 'confirm_password')

    def validate_email(self, value):
        if value is None:
            raise CustomValidation({'email': "Email Field is should not be empty"})
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')            
        if password != confirm_password:
            raise serializers.ValidationError({"message": "Password and confirm Password is Not Matching"})
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"message": "Email Already Exists Please Go with another Email"})
        return attrs

    def create(self, validated_data):
        confirm_password = validated_data.pop('confirm_password')
        user = Account.objects.create_user(
            email=validated_data['email'],
            username=generate_user(),
            fullname=validated_data['fullname'],
            password=validated_data['password']
        )
        return user
    

class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True, max_length=50)
    password = serializers.CharField(required=True, max_length=50)
    