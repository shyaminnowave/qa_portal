from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

# Create your models here.

User = get_user_model()

class Project(TimeStampedModel):

    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='logo')
    description = models.TextField()
    account = models.ForeignKey(User, on_delete=models.CASCADE, to_field='email', related_name='projects')
    project_key = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Projects'
        verbose_name_plural = 'Projects'
    

class ProjectIntegration(TimeStampedModel):

    class IntegrationChoice(models.TextChoices):
        JIRA = 'jira', _('JIRA')
        CONFLUENCE = 'confluence', _('Confluence')

    key = models.CharField(max_length=20, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                related_name='integrations')
    integration_type = models.CharField(choices=IntegrationChoice.choices, max_length=20,
                                default=IntegrationChoice.JIRA)
    domain_url = models.URLField()
    username = models.EmailField(_('Email'), max_length=50)
    token = models.CharField(_('token'), max_length=255)
    is_active = models.BooleanField(_('active'), default=True)

    def __str__(self):
        return self.project.name

    class Meta:
        verbose_name = 'Integration'
        verbose_name_plural = 'Integrations'
