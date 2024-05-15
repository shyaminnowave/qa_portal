import re
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
from apps.stbs.models import Language, Natco, STBManufacture
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
import json
from ckeditor.fields import RichTextField
# Create your models here.

User = get_user_model()


class TestCaseModel(TimeStampedModel):

    # class PriorityChoice(models.TextChoices):
    #     CLASSTHREE = 'class_3', _('Class 3')

    TODO = 'todo'
    ONGOING = 'ongoing'
    COMPLETED = 'completed'

    AUTOMATABLE = 'automatabel'
    NOT_AUTOMATABLE = 'not-automatable'
    IN_DEVELOPMENT = 'in-development'
    REVIEW = 'review'
    READY = 'ready'

    PERFORMANCE = 'performance'
    SOAK = 'soak'
    SMOKE = 'smoke'
    
    AUTOMATION_CHOICES = (
        (NOT_AUTOMATABLE, 'Not-Automatable'),  #automatable
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

    TESTCASE_CHOICES = (
        (PERFORMANCE, 'performance'),
        (SOAK, 'soak'),
        (SMOKE, 'smoke')
    )

    jira_id = models.IntegerField(_("Jira Id"), primary_key=True, unique=True, help_text=("Jira Id"))
    test_name = models.CharField(_("Test Report Name"), max_length=255, help_text=("Please Enter the TestCase Name"))
    priority = models.CharField(max_length=20, default='Class 3')
    jira_summary = models.TextField(_("Jira Summary"))
    test_description = models.TextField(_('TestCase Description'))
    testcase_type = models.CharField(choices=TESTCASE_CHOICES, max_length=20, default=PERFORMANCE)
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
        ordering = ['-jira_id',]

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self) -> str:
        return '%s' % self.test_name

    def get_jira_id(self) -> str:
        return 'TTVTM - %s' % self.jira_id
    
    def get_status(self) -> str:
        return '%s' % self.status


class NatcoStatus(TimeStampedModel):

    IN_DEVELOPMENT = 'in_development'
    NOT_AUTOMATABLE = 'not_automatable'
    MANUAL = 'manual'
    COMPLETE = 'complete'
    READY = 'READY'

    STATUS_CHOICES = (
        (IN_DEVELOPMENT, 'IN Development'),
        (NOT_AUTOMATABLE, 'Not Automatable'),
        (MANUAL, 'Manual'),
        (COMPLETE, 'Complete'),
        (READY, 'Ready')
    )

    natco = models.ForeignKey(Natco, on_delete=models.CASCADE, related_name='natco_status')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    device = models.ForeignKey(STBManufacture, on_delete=models.CASCADE)
    test_case = models.ForeignKey(TestCaseModel, on_delete=models.CASCADE, related_name='natco_status')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=MANUAL)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_natco', blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='natco_reviewer', blank=True, null=True)
    modified = models.ForeignKey(User, on_delete=models.CASCADE, related_name='natoc_modified', blank=True, null=True)
    applicable = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Natco Status'
        verbose_name_plural = 'Natco Status'

    def __str__(self):
        return '%s' % self.test_case

    def save(self, **kwargs):
        status = self.status
        test_case = TestCaseModel.objects.get(jira_id=self.test_case.jira_id)
        if status == 'in_development':
            test_case.automation_status = 'in-development'
        elif status == 'review':
            test_case.automation_status = 'review'
        elif status == 'ready':
            test_case.automation_status = 'ready'
        test_case.save()
        super(NatcoStatus, self).save(**kwargs)


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



class TestResult(TimeStampedModel):

    run_type = models.CharField(max_length=200, default='')
    date = models.CharField(max_length=200, default='')
    iteration_number = models.CharField(max_length=200, default='')
    testcase = models.CharField(max_length=255, default='')
    cpu = models.CharField(max_length=200, default='')
    ram = models.CharField(max_length=200, default='')
    start_time = models.CharField(max_length=200, default='')
    end_time = models.CharField(max_length=200, default='')
    job_uid = models.CharField(max_length=255, default='')
    node_id = models.CharField(max_length=255, default='')
    failure_reason = models.TextField()
    result = models.CharField(max_length=200, default='pass')
    natco = models.CharField(max_length=200, default='')
    load_time = models.CharField(max_length=200, default='')
    cpu_usage = models.CharField(max_length=200, default='')
    ram_usage = models.CharField(max_length=200, default='')
    country_code = models.CharField(max_length=200, default='')
    stb_release = models.CharField(max_length=200, default='')
    stb_firmware = models.CharField(max_length=200, default='')
    stb_android = models.CharField(max_length=200, default='')
    stb_build = models.CharField(max_length=255, default='')
    natco_node = models.CharField(max_length=200, default='')
    comment = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.testcase

    @property
    def get_start_time(self):
        start_time = re.findall(r'\b\d{2}:\d{2}:\d{2}\b', self.start_time)
        return start_time[0]

    @property
    def get_end_time(self):
        end_time = re.findall(r'\b\d{2}:\d{2}:\d{2}\b', self.end_time)
        return end_time[0]

    @classmethod
    def get_unique_node(cls):  
        natco_node = cls.objects.values_list('natoc_node', flat=True).distinct()
        return natco_node

    @classmethod
    def get_unique_natco_type(cls):
        natco_type = cls.objects.values_list('natco', flat=True).distinct()
        return natco_type
    
    @classmethod
    def get_unique_stb_release(cls):  
        stb_release = cls.objects.values_list('stb_release', flat=True).distinct()
        return stb_release

    @classmethod
    def get_unique_stb_android(cls):
        stb_android = cls.objects.values_list('stb_android', flat=True).distinct()
        return stb_android
    
    @classmethod
    def get_unique_stb_firmware(cls):  
        stb_firmware = cls.objects.values_list('stb_firmware', flat=True).distinct()
        return stb_firmware
    
    @classmethod
    def get_unique_filters(cls):
        _filter = {
            'natco_node': cls.objects.values_list('natco_node', flat=True).distinct(),
            'natco_type': cls.objects.values_list('natco', flat=True).distinct(),
            'stb_release': cls.objects.values_list('stb_release', flat=True).distinct(),
            'stb_android': cls.objects.values_list('stb_android', flat=True).distinct(),
            'stb_firmware': cls.objects.values_list('stb_firmware', flat=True).distinct()
        }
        return _filter


class Organization(TimeStampedModel):

    name = models.CharField(max_length=200)
    address = models.TextField()
    contact_info = models.CharField(max_length=200)


class ProjectInfo(TimeStampedModel):

    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    owner = models.ForeignKey(Organization, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)


class TestPlan(TimeStampedModel):

    name = models.CharField(max_length=200)
    project = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    owner = models.ForeignKey(Organization, on_delete=models.CASCADE)
    status = models.BooleanField()


class TestRun(TimeStampedModel):

    testcase = models.ForeignKey(TestCaseModel, on_delete=models.CASCADE)
    tester = models.ForeignKey(User, on_delete=models.CASCADE)
    execution_date = models.DateField()
    execution_time = models.TimeField()
    status = models.BooleanField()
    actual_results = models.CharField(max_length=200)
    comments = models.CharField(max_length=200)


class Defects(TimeStampedModel):

    testrun = models.ForeignKey(TestRun, on_delete=models.CASCADE)
    severity = models.CharField(max_length=200)
    priority = models.CharField(max_length=200)
    status = models.BooleanField()
    assigned = models.ForeignKey(User, on_delete=models.CASCADE, related_name='defects_assigned')
    reported = models.ForeignKey(User, on_delete=models.CASCADE, related_name='defects_reported')
    reported_date = models.DateField()


class TestEnv(TimeStampedModel):

    name = models.CharField(max_length=200)
    description = models.TextField()
    configuration_details = models.TextField()


class TestCycle(TimeStampedModel):

    name = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    owner = models.ForeignKey(Organization, on_delete=models.CASCADE)
    status = models.BooleanField()


class TestSuit(TimeStampedModel):

    name = models.CharField(max_length=200)
    description = models.TextField()
    testplan = models.ForeignKey(TestPlan, on_delete=models.CASCADE)


class TestRelease(TimeStampedModel):

    name = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    owner = models.ForeignKey(Organization, on_delete=models.CASCADE)
    status = models.BooleanField()
