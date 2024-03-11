from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _

# Create your models here.

class TestCaseModel(TimeStampedModel):
    test_name = models.CharField(_("Test Report Name"), max_length=255,
                                   help_text=("Please Enter the TestCase Name"))
    
    jira_id = models.IntegerField(_("Jira Id"), unique=True, help_text=("Jira Id"))
    jira_summary = models.TextField(_("Jira Summary"))
    test_description = models.TextField(_("Test description"))

    class Meta:
        verbose_name = 'TestCase'
        verbose_name_plural = 'TestCases'

    def __str__(self) -> str:
        return self.test_name

    def get_jira_id(self) -> str:
        return 'TTVTM - %s' % self.jira_id
    

class TestCaseStep(TimeStampedModel):
    testcase = models.ForeignKey(TestCaseModel, on_delete=models.CASCADE, related_name='test_steps')
    step_id = models.IntegerField(_("step number"))
    step_data = models.TextField(_('Testing Parameters'))
    step_description = models.TextField()

    def __str__(self):
        return '%s - %s' % (self.testcase.test_name, self.step_id)
    
