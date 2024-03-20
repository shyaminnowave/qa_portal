from rest_framework.views import Response
from rest_framework import generics
from apps.testcase_app.models import TestCaseModel, TestCaseStep
from apps.testcase_app.apis.serializers import TestCaseSerializerList, TestCaseSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import permission_classes
from apps.testcase_app.pagination import CustomPagination

class TestCaseListView(generics.ListAPIView):

    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = TestCaseModel.objects.all()
    serializer_class = TestCaseSerializerList
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
class TestCaseView(generics.CreateAPIView):

    serializer_class = TestCaseSerializer


class TestCaseDetailView(generics.RetrieveUpdateDestroyAPIView):

    lookup_field = 'jira_id'
    serializer_class = TestCaseSerializer
    queryset = TestCaseModel.objects.all()
    
    def get_object(self):
        queryset = get_object_or_404(TestCaseModel, jira_id=self.kwargs.get('jira_id'))
        return queryset
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({"success": True, "data": response.data})

