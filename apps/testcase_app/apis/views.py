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
from rest_framework.filters import SearchFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class TestCaseListView(generics.ListAPIView):

    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = TestCaseModel.objects.all()
    serializer_class = TestCaseSerializerList
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ['jira_id', 'test_name', 'natcos', 'status', 'automation_status']

    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TestCaseView(generics.CreateAPIView):

    serializer_class = TestCaseSerializer

    @swagger_auto_schema(
        request_body=TestCaseSerializer,  # Assuming TestCaseSerializer handles request body
        manual_parameters=[
            openapi.Parameter('Status', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                              enum=[TestCaseModel.TODO, TestCaseModel.ONGOING, TestCaseModel.COMPLETED],
                              description="Dropdown 1 description"),
            openapi.Parameter('Automation Status', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                              enum=[TestCaseModel.NOTAUTOMATABLE, TestCaseModel.INDEVELOPMENT, TestCaseModel.READY,
                                    TestCaseModel.REVIEW, TestCaseModel.COMPLETED],
                              description="Dropdown 2 description"),
        ]
    )
    def post(self, request, *args, **kwargs):
        return super(TestCaseView, self).post(request, *args, **kwargs)


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

