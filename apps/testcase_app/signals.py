from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.testcase_app.models import TestCaseModel, TestCaseStep


@receiver(post_save)
def capture_request_info(sender, instance, created, **kwargs):
    if isinstance(instance, TestCaseModel):
        history_type = 'created' if created else 'modified'
        request_method = kwargs.get('request_method')
        request_user = kwargs.get('request_user')
        instance.create_historical_record(history_type=history_type, request_method=request_method, history_user=request_user)



@receiver(post_save)
def capture_request_step_info(sender, instance, created, **kwargs):
    if isinstance(instance, TestCaseStep):
        history_type = 'created' if created else 'modified'
        request_method = kwargs.get('request_method')
        request_user = kwargs.get('request_user')
        instance.create_historical_record(history_type=history_type, request_method=request_method, history_user=request_user)
