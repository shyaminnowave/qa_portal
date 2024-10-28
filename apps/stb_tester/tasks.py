from celery import shared_task
from apps.stb_tester.models import StbResult
from apps.stb_tester.views import StbAPI
from apps.testcases.models import TestCaseModel, AutomationChoices
from django.db import transaction


@shared_task()
def get_stb_result(stb=StbAPI()):
    queryset = TestCaseModel.objects.exclude(automation_status=AutomationChoices.NOT_AUTOMATABLE)
    _result = []
    _cached_test = {}
    try:
        for i in queryset:
            if i.test_name not in _cached_test:
                _cached_test[i.test_name] = i
            __result_instance = StbResult.objects.filter(testcase=i).last()
            if __result_instance:
                response = stb.get_result(testcase=i.test_name, date=__result_instance.get_start_date())
            else:
                response = stb.get_result(i.test_name)
            if response is not None:
                for j in response:
                    _data = {
                        "result_id": j['result_id'],
                        "result_url": j['result_url'],
                        "triage_url": j['triage_url'],
                        "job_uid": j['job_uid'],
                        "start_time": j['start_time'],
                        "end_time": j['end_time'],
                        "testcase": _cached_test[i.test_name],
                        "result": j['result'],
                        "failure_reason": j['failure_reason']
                    }
                    _result.append(StbResult(**_data))
                with transaction.atomic():
                    StbResult.objects.bulk_create(_result, ignore_conflicts=True)
    except Exception as e:
        return str(e)




