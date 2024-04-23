
from typing import Any
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import UserManager, Group


class CustomUserManager(UserManager):
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        user = super(CustomUserManager, self).create_user(username, email, password, **extra_fields)
        guest_group, _ = Group.objects.get_or_create(name='Guest')
        user.groups.add(guest_group)
        return user
