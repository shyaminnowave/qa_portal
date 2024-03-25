from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
# Create your models here.contrib.


class Account(AbstractBaseUser, PermissionsMixin, TimeStampedModel):

    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        _('email address'), 
        max_length=200, 
        unique=True, 
        help_text=_("Required a Valid EmailAddress"),
        error_messages={
            'unique': _("A user with this EmailId already Exists")
        }

    )
    username = models.CharField(_('username'), max_length=30, validators=[username_validator])
    fullname = models.CharField(_('fullname'), max_length=30)
    is_staff = models.BooleanField(
        _('staff status'), default=False, help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(_("_active"), default=True, help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")

    def get_full_name(self):
        return self.fullname
    
    def get_short_name(self):
        name = self.fullname.split()
        return name
    

class LoginHistory(models.Model):

    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='login_history')
    ip = models.CharField(max_length=15, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    is_login = models.BooleanField(default=True, null=True, blank=True)
    is_logged_in = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.id} - {self.user} - {self.ip}"

    def __eq__(self, other: object) -> bool:
        return self.ip == other.ip and self.user_agent == other.user_agent

    def __hash__(self) -> int:
        return hash(('ip', self.ip, 'user_agent', self.user_agent))

    class Meta:
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Historys'
        