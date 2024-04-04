from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
from apps.stbs.models import Language, Natco, STBManufacture
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
import json
# Create your models here.

User = get_user_model()


class TestCaseModel(TimeStampedModel):

    TODO = 'todo'
    ONGOING = 'ongoing'
    COMPLETED = 'completed'

    AUTOMATABLE = 'automatabel'
    NOT_AUTOMATABLE = 'not-automatable'
    IN_DEVELOPMENT = 'in-development'
    REVIEW = 'review'
    READY = 'ready'
    
    AUTOMATION_CHOICES = (
        (NOT_AUTOMATABLE, 'Not-Automatable'), #automatable
        (IN_DEVELOPMENT, 'In-Development'),
        (REVIEW, 'Review'),
        (READY, 'Ready'),
        (COMPLETED, 'Completed')
    )

    STATUS_CHOICES = (
        (TODO, 'Todo'),
        (ONGOING, 'On-Going'),
        (COMPLETED, 'Completed')
    )

    jira_id = models.IntegerField(_("Jira Id"), primary_key=True, unique=True, help_text=("Jira Id"))
    test_name = models.CharField(_("Test Report Name"), max_length=255, help_text=("Please Enter the TestCase Name"))
    jira_summary = models.TextField(_("Jira Summary"))
    test_description = models.TextField(_("Test description"))
    comments = models.TextField(blank=True, null=True)
    defects = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ONGOING)
    script_name = models.CharField(max_length=50, blank=True, null=True)
    script = models.CharField(max_length=255, blank=True, null=True)
    automation_status = models.CharField(max_length=20, choices=AUTOMATION_CHOICES, default=AUTOMATABLE)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'TestCase'
        verbose_name_plural = 'TestCases'

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self) -> str:
        return "%s - %s" % (self.test_name, self.jira_id)

    def get_jira_id(self) -> str:
        return 'TTVTM - %s' % self.jira_id
    
    def get_status(self) -> str:
        return self.status

    # @classmethod
    # def create_historical_record(cls, instance, history_type, history_record=None, **kwargs):
    #     history_record = super().create_historical_record(instance, history_record, **kwargs)
    #     request_user = kwargs.get('history_user')
    #     request_method = kwargs.get('request_method')
    #     history_record.request_user = request_user.username if request_user else None
    #     history_record.request_method = request_method
    #     history_record.save()
    #     return history_record


class NatcoStatus(TimeStampedModel):

    natco = models.ForeignKey(Natco, on_delete=models.CASCADE, related_name='natco_status')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    test_case = models.ForeignKey(TestCaseModel, on_delete=models.CASCADE)
    device = models.ForeignKey(STBManufacture, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    modified = models.ForeignKey(User, on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self):
        return self.natco.natco


class TestCaseStep(TimeStampedModel):

    TODO = 'todo'
    ONGOING = 'ongoing'
    COMPLETED = 'completed'

    STATUS_CHOICES = (
        (TODO, 'Todo'),
        (ONGOING, 'On-Going'),
        (COMPLETED, 'Completed')
    )

    testcase = models.ForeignKey(TestCaseModel, on_delete=models.CASCADE, related_name='test_steps', blank=True,
                                 null=True)
    step_id = models.IntegerField(_("step number"), blank=True, null=True)
    step_data = models.TextField(_('Testing Parameters'), blank=True, null=True)
    step_description = models.TextField(blank=True, null=True)
    excepted_result = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=TODO)
    history = HistoricalRecords()

    # @classmethod
    # def create_historical_record(cls, instance, history_type, history_record=None, **kwargs):
    #     history_record = super().create_historical_record(instance, history_record, **kwargs)
    #     request_user = kwargs.get('history_user')
    #     request_method = kwargs.get('request_method')
    #     history_record.request_user = request_user.username if request_user else None
    #     history_record.request_method = request_method
    #     history_record.save()
    #     return history_record

    # def __str__(self):
    #     return '%s - %s' % (self.testcase.test_name, self.step_id)
    

