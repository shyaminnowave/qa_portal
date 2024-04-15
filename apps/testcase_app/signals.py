from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.testcase_app.models import TestCaseModel, TestCaseStep, NatcoStatus
from apps.stbs.models import NactoManufactureLanguage
from django.db import transaction


@receiver(post_save, sender=TestCaseModel)
def save_natco_status(sender, instance, created, **kwargs):
    _data = []
    natco = NactoManufactureLanguage.objects.all()
    testcase_instance = TestCaseModel.objects.filter(jira_id=instance.jira_id)
    if testcase_instance is None:
        for data in natco:
            _data.append(NatcoStatus(natco=data.natco, language=data.language_name, device=data.device_name,
                                     test_case=instance))
        try:
            with transaction.atomic():
                NatcoStatus.objects.bulk_create(_data)
        except Exception as e:
            print(e)


