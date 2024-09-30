from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.testcases.models import TestCaseModel, TestCaseStep, NatcoStatus, ScriptIssue, AutomationChoices
from apps.stbs.models import NactoManufacturesLanguage
from django.db import transaction
from django.shortcuts import get_object_or_404


@receiver(post_save, sender=TestCaseModel)
def save_natco_status(sender, instance, created, **kwargs):
    _data = []
    natco = NactoManufacturesLanguage.objects.all()
    if created == True:
        for data in natco:
            _data.append(NatcoStatus(natco=data.natco, language=data.language_name, device=data.device_name,
                                         test_case=instance))
        try:
            with transaction.atomic():
                NatcoStatus.objects.bulk_create(_data)
        except Exception as e:
            print(e)
    else:
        pass


@receiver(post_save, sender=ScriptIssue)
def change_testcase_status(sender, instance, created, **kwargs):
    try:
        _instance = TestCaseModel.objects.get(pk=instance.testcase.id)
        if _instance:
            if instance.status == 'open':
                _instance.automation_status = AutomationChoices.IN_DEVELOPMENT
            elif instance.status == 'closed':
                _testcase = ScriptIssue.check_open_issues()
                if _testcase is False:
                    _instance.automation_status = AutomationChoices.REVIEW
            _instance.save()
        else:
            print('not found')
    except TestCaseModel.DoesNotExist as e:
            return e


