
from typing import Any
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import UserManager

class CustomUserManager(UserManager): ...