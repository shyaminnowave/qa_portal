from rest_framework.views import Response
from rest_framework import generics
from apps.testcase_app.models import TestCaseModel, TestCaseStep
from apps.testcase_app.apis.serializers import TestCaseSerializerList, TestCaseSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


class CustomRenderer(Response):

    def __init__(self, data=None, status=None, template_name=None, headers=None, exception=False, content_type=None):
        super().__init__(data, status, template_name, headers, exception, content_type)
        if data is not None:
            self.data['success'] = True

    
class TestCaseListView(generics.ListAPIView):

    queryset = TestCaseModel.objects.all()
    serializer_class = TestCaseSerializerList

    def get(self, request, *args, **kwargs):
        super().list(request, *args, **kwargs)
    
class TestCaseView(generics.CreateAPIView):

    serializer_class = TestCaseSerializer


class TestCaseDetailView(generics.RetrieveUpdateDestroyAPIView):

    lookup_field = 'pk'
    serializer_class = TestCaseSerializer
    
    def get_object(self):
        queryset = get_object_or_404(TestCaseModel, id=self.lookup_field)


