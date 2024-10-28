from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.testcases.models import TestCaseModel, NatcoStatus, ScriptIssue, AutomationChoices
from apps.stbs.models import NactoManufacturesLanguage, Natco
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


@receiver(post_save, sender=TestCaseModel)
def script_natcostatus(sender, instance, created, **kwargs):
    natcos = Natco.objects.all()
    _natco_status = []
    if instance.automation_status != AutomationChoices.NOT_AUTOMATABLE:
        _instance = NatcoStatus.objects.filter(test_case=instance)
        if not _instance:
            _data = {}
            for data in natcos:
                for manufacture in data.manufacture.all():
                    for language in data.language.all():
                        _data = {
                            "natco": data.natco,
                            "language": language.language_name,
                            "device": manufacture.name,
                        }
                        print(_data)
                        _natco_status.append(NatcoStatus(
                            natco=data.natco, language=language.language_name, device=manufacture.name,
                            test_case=instance
                        ))
            with transaction.atomic():
                NatcoStatus.objects.bulk_create(_natco_status)
        else:
            print('D')


@receiver(post_save, sender=ScriptIssue)
def change_testcase_status(sender, instance, created, **kwargs):
    try:
        _instance = TestCaseModel.objects.get(pk=instance.testcase.id)
        if _instance:
            if instance.status == 'open':
                _instance.automation_status = AutomationChoices.IN_DEVELOPMENT
            elif instance.status == 'under_review':
                _instance.automation_status = AutomationChoices.REVIEW
            elif instance.status == 'closed':
                _testcase = ScriptIssue.check_open_issues(instance=instance.testcase)
                if _testcase is False:
                    _instance.automation_status = AutomationChoices.READY
            _instance.save()
        else:
            print('not found')
    except TestCaseModel.DoesNotExist as e:
            return e


