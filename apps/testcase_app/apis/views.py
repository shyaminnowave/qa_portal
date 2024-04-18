from rest_framework.views import Response
from rest_framework import generics
from apps.testcase_app.models import TestCaseModel, TestCaseStep, NatcoStatus
from apps.testcase_app.apis.serializers import TestCaseSerializerList, TestCaseSerializer, ExcelSerializer, \
        NatcoStatusSerializer
from apps.stbs.models import NactoManufactureLanguage
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.testcase_app.pagination import CustomPagination
from openpyxl import load_workbook
from django.db import transaction
from django.forms.models import model_to_dict
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiSchemaBase
from drf_spectacular.openapi import OpenApiTypes, OpenApiExample
from rest_framework.exceptions import APIException
from django_filters import rest_framework as filters
from apps.testcase_app.filters import NatcoStatusFilter
from rest_framework import status


class ExcelErrorException(APIException):

    default_detail = "Cannot Import Excel file. Please Check the Data"
    default_code = "error"


class TestCaseListView(generics.ListAPIView):

    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = TestCaseModel.objects.all()
    serializer_class = TestCaseSerializerList
    pagination_class = CustomPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ('jira_id', 'test_name', 'status', 'automation_status')

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return super().list(request, *args, **kwargs)


class TestCaseView(generics.CreateAPIView):

    serializer_class = TestCaseSerializer

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


class TestCaseNatcoView(generics.ListAPIView):

    serializer_class = NatcoStatusSerializer
    model = NatcoStatus.objects.all()
    lookup_field = 'jira_id'
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = NatcoStatus.objects.filter(test_case_id=self.kwargs.get('jira_id'))
        return queryset


class TestCaseNatcoList(generics.ListAPIView):

    serializer_class = NatcoStatusSerializer
    queryset = NatcoStatus.objects.all()
    filterset_class = NatcoStatusFilter
    pagination_class = CustomPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(name='Natco', description="Enter the Natco", required=False, type=OpenApiTypes.STR,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name='language', description="Enter the Language", required=False, type=OpenApiTypes.STR,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name='device', description="Enter the Device", required=False, type=OpenApiTypes.STR,
                             location=OpenApiParameter.QUERY),
        ]
    )
    def list(self, request, *args, **kwargs):
        data = self.get_queryset()
        filter_set = self.filterset_class(request.GET, self.get_queryset())
        if filter_set.is_valid():
            data = filter_set.qs
        paginated_data = self.paginate_queryset(data)
        serializer = self.get_serializer(paginated_data, many=True)
        try:
            if serializer:
                return self.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"success": False, "data": str(e)})


class TestCaseNatcoDetail(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = NatcoStatusSerializer
    queryset = NatcoStatus.objects.all()
    lookup_field = 'pk'
    
    def patch(self, request, *args, **kwargs):
        response = super(TestCaseNatcoDetail, self).patch(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return Response({'success': True, "data": response.data})
        return Response({"success": False, "error": "Field Not Updated"})


class GetExcel(generics.GenericAPIView):

    serializer_class = ExcelSerializer

    def post(self, request, *args, **kwargs):
        file_uploaded = request.FILES.get("file")
        wb = load_workbook(file_uploaded)
        ws = wb.active
        test_case = None
        _data = dict()
        _step_data = dict()
        testcase_list = []
        step_list = []
        natco_list = []
        natco = NactoManufactureLanguage.objects.all()
        try:
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0] is not None:
                    jira_id_parts = row[0].split('-')
                    _data = {
                        "jira_id": jira_id_parts[-1],
                        "jira_summary": row[1],
                        "test_description": row[2],
                        "test_name": "TestCase"
                    }
                    testcase_list.append(TestCaseModel(**_data))
                    test_case = jira_id_parts[-1]
                    for data in natco:
                        natco_list.append(NatcoStatus(natco=data.natco, language=data.language_name,
                                                      device=data.device_name, test_case_id=test_case))
                elif row[0] is None and row[5] is not None:
                    _step_data = {
                        "testcase_id": test_case,
                        "step_id": int(row[5]),
                        "step_description": row[6],
                        "step_data": row[7],
                        "excepted_result": row[8]
                    }
                    step_list.append(TestCaseStep(**_step_data))
            with transaction.atomic():
                TestCaseModel.objects.bulk_create(testcase_list)
                TestCaseStep.objects.bulk_create(step_list)
                NatcoStatus.objects.bulk_create(natco_list)
        except Exception as e:
            return Response({"success": False, "error": "Data Format Error"})
        return Response({"success": True, "data": "TestCase Added Successfull"})
