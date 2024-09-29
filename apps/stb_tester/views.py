from rest_framework.views import APIView, Response
from apps.stb_tester.models import StbResult
from apps.stb_tester.utlity import StbAPI
from apps.testcases.models import TestCaseModel, AutomationChoices
from apps.stb_tester.serializers import ResultSerializer
from django.db import transaction
from rest_framework import status, generics
from analytiqa.helpers.renders import ResponseInfo


class StbTestCaseResult(generics.ListAPIView):

    serializer_class = ResultSerializer

    def get_queryset(self):
        testcase = self.kwargs['id']
        queryset = StbResult.objects.filter(testcase__id=testcase).order_by('-start_time')[:50]
        return queryset

    def list(self, request, *args, **kwargs):
        return super(StbTestCaseResult, self).list(request, *args, **kwargs)
