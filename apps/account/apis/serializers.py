from rest_framework import serializers
from apps.account.models import Account
from rest_framework.views import exception_handler
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from apps.account.utils import generate_user
from django.core.exceptions import ValidationError
from rest_framework.fields import CharField
from apps.account.fields import CompanyEmailValidator
import re
from django.contrib.auth.models import Group, PermissionsMixin

User = get_user_model()


class CompanyMail(CharField):
    default_error_messages = {
        'invalid': _('Enter a valid email address.')
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        validator = CompanyEmailValidator(message=self.error_messages['invalid'])
        self.validators.append(validator)


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

    email = CompanyMail(required=True, max_length=30)
    fullname = serializers.CharField(required=True, max_length=30)
    password = serializers.CharField(required=True, max_length=20)
    confirm_password = serializers.CharField(required=True, max_length=20, write_only=True)
        
    class Meta:
        model = User
        fields = ('email', 'fullname', 'password', 'confirm_password')

    def validate_email(self, value):
        if value is None:
            raise CustomValidation({'email': "Email Field is should not be empty"})
        elif value:
            user_part, doamin_part = value.rsplit('@', 1)
            host, domain = doamin_part.rsplit('.', 1)
            if host == 'innowave' and domain == 'tech':
                return value
            raise CustomValidation({"email": "Please Enter you Innowave Mail"})

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


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'

    def to_representation(self, instance):
        response = super(GroupSerializer, self).to_representation(instance)
        response['permissions'] = [i.name for i in instance.permissions.all()]
        return response


class ProfileSerializer(serializers.ModelSerializer):

    groups = GroupSerializer(required=False, read_only=True, many=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'groups']


class UsernameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ('username',)


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['fullname', 'email', 'username', 'is_staff', 'is_superuser']

