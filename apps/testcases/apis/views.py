from rest_framework import generics
from collections import defaultdict
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.testcases.models import (
    TestCaseModel,
    TestCaseStep,
    NatcoStatus,
    TestcaseExcelResult,
    TestCaseChoices,
    AutomationChoices,
    StatusChoices,
    PriorityChoice,
    TestReport, Comment, ScriptIssue, TestCaseScript, TestCaseMetaData, TestPlanning
)
from apps.testcases.apis.serializers import (
    TestCaseSerializerList,
    TestCaseSerializer,
    ExcelSerializer,
    NatcoStatusSerializer,
    DistinctTestResultSerializer,
    NavbarFilterSerializer,
    TestResultDRPSerializer,
    BulkFieldUpdateSerializer,
    NatcoGraphAPISerializer,
    GraphReportSerializer,
    TestStepSerializer,
    HistorySerializer,
    ScriptIssueSerializer,
    CommentSerializer,
    TestcaseScriptSerializer,
    TestMetaDataSerializer,
    TestPlanningSerializer
)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.testcases.pagination import CustomPagination, CustomPageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiSchemaBase
from django_filters import rest_framework as filters
from apps.testcases.filters import NatcoStatusFilter, TestCaseFilter
from analytiqa.helpers.renders import ResponseInfo
from analytiqa.helpers import custom_generics as cgenerics
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Min, F, Count, Subquery, OuterRef, Avg, Q
from apps.stbs.models import Natco
from apps.testcases.utlity import ReportExcel, UserStoryExcel, TestcaseMetaExcel, TestCaseDemoExcel
# from apps.stb_tester.views import BaseAPI


class ResponseTemplateApi:

    def __init__(self, instance):
        self.response_format = ResponseInfo().response
        self.instance = instance

    def response(self):
        if self.instance == True:
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = "Success"
            self.response_format["message"] = "Success"
            return self.response_format
        else:
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "error"
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Bulk update fields for test cases or NATCO entities",
    description=(
        "This endpoint allows for bulk updates of specific fields in test cases or NATCO entities.\n\n"
        "**Path Parameters:**\n"
        "- `status`: Updates the status of test cases.\n"
        "- `automation-status`: Updates the automation status of test cases.\n"
        "- `natco/status`: Updates the status of NATCO entities.\n\n"
        "**Request Body:**\n"
        "The body should contain the fields to be updated. The exact fields depend "
        "on the operation being performed.\n\n"
        "**Responses:**\n"
        "- `200 OK`: Successfully updated the specified fields.\n"
        "- `400 Bad Request`: Returned if the provided data is invalid or if the update operation fails."
    ),
    tags=["TestCase Module APIS"]
)
class BulkFieldUpdateView(generics.GenericAPIView):

    serializer_class = BulkFieldUpdateSerializer

    def patch(self, request, *args, **kwargs):
        kwargs_splitted = kwargs.get("path").split("/")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            match kwargs_splitted[0]:
                case "status":
                    instance = serializer.update_testcase_status(
                        serializer.validated_data
                    )
                case "automation-status":
                    instance = serializer.update_testcase_automation(
                        serializer.validated_data
                    )
                case "natco":
                    match kwargs_splitted[1]:
                        case "status":
                            instance = serializer.update_natco_status(
                                serializer.validated_data
                            )
                        case _:
                            instance = False
                case _:
                    instance = False
            response_template = ResponseTemplateApi(instance)
            return Response(
                response_template.response(),
                status=status.HTTP_200_OK if instance else status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "status": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid data",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(
    summary="Retrieve a list of test cases",
    description=(
        "This endpoint retrieves a paginated list of test cases.\n\n"
    ),
    tags=["TestCase Module APIS"]
)
class TestCaseListView(generics.ListAPIView):

    # authentication_classes = [JWTAuthentication]
    # permission_classes = [AdminPermission]
    serializer_class = TestCaseSerializerList
    pagination_class = CustomPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = TestCaseFilter
    filterset_fields = [
        "jira_id",
        "test_name",
        "status",
        "priority",
        "automation_status",
    ]

    def get_queryset(self):
        queryset = None
        project = self.kwargs.get("project", None)
        if self.kwargs.get('type') == 'performance':
            queryset = TestCaseModel.objects.filter(project=project).performance_testcase()
        elif self.kwargs.get('type') == 'smoke':
            queryset = TestCaseModel.objects.filter(project=project).smoke_testcase()
        elif self.kwargs.get('type') == 'soak':
            queryset = TestCaseModel.objects.filter(project=project).soak_testcase()
        return queryset.only("jira_id",
                            "test_name",
                            "priority",
                            "testcase_type",
                            "status",
                            "automation_status",).all()

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)
        return response


@extend_schema(
    summary="Create a new test case",
    description=(
        "This endpoint allows you to create a new test case.\n\n"
    ),
    tags=["TestCase Module APIS"]
)
class TestCaseView(cgenerics.CustomCreateAPIView):

    authentication_classes = (JWTAuthentication, )
    serializer_class = TestCaseSerializer

    def post(self, request, *args, **kwargs):
        self.response_format['message'] = "TestCase Created Successfull"
        return super(TestCaseView, self).post(request, *args, **kwargs)

    def get_serializer_context(self, **kwargs):
        return {
            "request": self.request
        }


@extend_schema(
    summary="Retrieve, update, or delete a test case",
    description=(
        "This endpoint allows you to retrieve, update, or delete a test case by its ID.\n\n"
    ),
    tags=["TestCase Module APIS"]
)
class TestCaseDetailView(cgenerics.CustomRetrieveUpdateDestroyAPIView):

    authentication_classes = [JWTAuthentication,]
    lookup_field = "id"
    serializer_class = TestCaseSerializer

    def get_object(self):
        queryset = get_object_or_404(
            TestCaseModel.objects.prefetch_related("test_steps"),
            id=self.kwargs.get("id"),
        )
        # natco = queryset.annotate(natco_status=Subquery(NatcoStatus.objects.select_related('test_case', 'language',
        # 'device', 'natco', 'user').filter(test_case_id=self.kwargs.get('jira_id'))))
        return queryset

    def get_serializer_context(self):
        return {
            "request": self.request
        }

    def get(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        # queryset = NatcoStatus.objects.select_related(
        #     "test_case", "language", "device", "natco", "user"
        # ).filter(test_case_id=self.kwargs.get("jira_id"))
        # serializer = NatcoStatusSerializer(queryset, many=True)
        # response.data["natco_status"] = serializer.data
        return response
    
    def put(self, request, *args, **kwargs):
        return super(TestCaseDetailView, self).put(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return super(TestCaseDetailView, self).patch(request, *args, **kwargs)


@extend_schema(
    summary="Create or update a test case step",
    description=(
        "This endpoint allows you to create a new test case step or update an existing one.\n\n"
    ),
    tags=["TestCase Module APIS"]
)
class TestCaseStepView(cgenerics.CustomCreateAPIView, cgenerics.CustomUpdateAPIView):

    serializer_class = TestStepSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid(raise_exception=True):
                serializer.create(serializer.validated_data)
                self.response_format['status'] = status.HTTP_201_CREATED
                self.response_format['data'] = serializer.data
                self.response_format['message'] = 'Success'
                return Response(self.response_format, status=status.HTTP_201_CREATED)
            self.response_format['status'] = status.HTTP_400_BAD_REQUEST
            self.response_format['data'] = 'Error'
            self.response_format['message'] = 'Error'
            return Response(self.response_format, status=status.HTTP_201_CREATED)
        except Exception as e:
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, *args, **kwargs):
        testcase_instance = TestCaseStep.objects.get(id=request.data['id'])
        serializer = self.get_serializer(instance=testcase_instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.update(instance=testcase_instance, validated_data=serializer.validated_data)
            self.response_format['status'] = status.HTTP_201_CREATED
            self.response_format['data'] = serializer.data
            self.response_format['message'] = 'Success'
            return Response(self.response_format, status=status.HTTP_201_CREATED)
        self.response_format['status'] = status.HTTP_400_BAD_REQUEST
        self.response_format['data'] = 'Error'
        self.response_format['message'] = 'Error'
        return Response(self.response_format, status=status.HTTP_201_CREATED)

    def delete(self, request):
        teststep_instance = TestCaseStep.objects.get(id=request.data.get('id'))
        serializer = self.get_serializer(instance=teststep_instance)
        serializer.delete()
        return Response({"success": True})


@extend_schema(
    summary="Delete a test step",
    description=(
        "This endpoint allows you to delete a specific test step by its ID.\n\n"
    ),
    tags=["TestCase Module APIS"]
)
class TestStepDeleteView(cgenerics.CustomDestroyAPIView):

    serializer_class = TestStepSerializer

    def delete(self, request, *args, **kwargs):
        teststep_instance = TestCaseStep.objects.get(id=kwargs.get('id'))
        serializer = self.get_serializer(instance=teststep_instance)
        serializer.delete(teststep_instance)
        return Response("success")


class TestCaseNatcoView(generics.ListAPIView):

    # permission_classes = [AdminPermission]
    serializer_class = NatcoStatusSerializer
    lookup_field = "id"
    pagination_class = CustomPageNumberPagination


    def get_queryset(self):
        queryset = (
            NatcoStatus.objects.select_related("test_case")
            .filter(test_case_id=self.kwargs.get("id"))
        )
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(TestCaseNatcoView, self).list(request, *args, **kwargs)
        return response

@extend_schema(
    summary="Retrieve NATCO statuses for a specific test case",
    description=(
        "This endpoint retrieves the NATCO statuses associated with a specific test case.\n\n"
        "**Path Parameters:**\n"
        "- `jira_id`: The unique identifier of the test case for which NATCO statuses are being queried.\n\n"
        "**Response:**\n"
        "- `200 OK`: A list of NATCO statuses, including the `id` and `summary` fields.\n"
        "- `404 Not Found`: Returned if no NATCO statuses are found for the specified test case."
    ),
    tags=["TestCase Module APIS"]
)
class TestCaseNatcoList(generics.ListAPIView):
    # permission_classes = [AdminPermission]
    serializer_class = NatcoStatusSerializer
    filterset_class = NatcoStatusFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = NatcoStatus.objects.select_related('test_case').all()
        return queryset

    # @extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             name="Natco",
    #             description="Enter the Natco",
    #             required=False,
    #             type=OpenApiTypes.STR,
    #             location=OpenApiParameter.QUERY,
    #         ),
    #         OpenApiParameter(
    #             name="Language",
    #             description="Enter the Language",
    #             required=False,
    #             type=OpenApiTypes.STR,
    #             location=OpenApiParameter.QUERY,
    #         ),
    #         OpenApiParameter(
    #             name="Device",
    #             description="Enter the Device",
    #             required=False,
    #             type=OpenApiTypes.STR,
    #             location=OpenApiParameter.QUERY,
    #         ),
    #         OpenApiParameter(
    #             name="Jira Id",
    #             description="Enter the Jira ID",
    #             required=False,
    #             type=OpenApiTypes.STR,
    #             location=OpenApiParameter.QUERY,
    #         ),
    #         OpenApiParameter(
    #             name="Applicable",
    #             description="Enter the Applicable",
    #             required=False,
    #             type=OpenApiTypes.BOOL,
    #             location=OpenApiParameter.QUERY,
    #         ),
    #         OpenApiParameter(
    #             name="status",
    #             description="Choose a Status",
    #             required=False,
    #             type=OpenApiTypes.STR,
    #             location=OpenApiParameter.QUERY,
    #             enum=NatcoStatus.NatcoStatusChoice.choices,
    #         ),
    #     ]
    # )
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


@extend_schema(
    summary="Retrieve, update, or delete a NATCO status",
    description=(
        "This endpoint allows for retrieving, updating, or deleting a NATCO status by its ID.\n\n"
        "**Path Parameters:**\n"
        "- `id`: The unique identifier of the NATCO status.\n\n"
        "**Responses:**\n"
        "- `200 OK`: Returns the requested NATCO status details when retrieved.\n"
        "- `204 No Content`: Indicates successful deletion of the NATCO status.\n"
        "- `400 Bad Request`: Returned when the update request is invalid.\n"
        "- `404 Not Found`: Returned if the specified NATCO status does not exist."
    ),
    tags=["TestCase Module APIS"]
)
class TestCaseNatcoDetail(cgenerics.CustomRetrieveUpdateDestroyAPIView):
    # permission_classes = [AdminPermission]
    serializer_class = NatcoStatusSerializer
    lookup_field = "pk"

    def get_object(self):
        queryset = NatcoStatus.objects.select_related("test_case").get(
            id=self.kwargs.get("pk")
        )
        return queryset

    def get_serializer_context(self):
        return {
            'request': self.request
        }


@extend_schema(
    summary="Retrieve Filter Options for Test Cases",
    description=(
        "This endpoint returns various filter options for test cases, including:\n\n"
        "- **Test Case Status**: A list of available status choices for test cases.\n"
        "- **Status**: A list of general status options.\n"
        "- **Priority**: A list of priority levels for test cases.\n"
        "- **Automation**: A list of automation-related options.\n\n"
        "Each filter option is represented as an object with `label` and `value` fields."
    ),
    tags=["TestCase Module APIS"]
)
class FiltersView(APIView):

    def get(self, request, *args, **kwargs):
        testcase_status = [{"label": choice.label, "value": choice.value} for choice in TestCaseChoices]
        status = [{"label": choice.label, "value": choice.value} for choice in StatusChoices]
        priority = [{"label": choice.label, "value": choice.value} for choice in PriorityChoice]
        automation = [{"label": choice.label, "value": choice.value} for choice in AutomationChoices]
        _data = {
            "testcase_filter": testcase_status,
            "status": status,
            "priority": priority,
            "automation": automation
        }
        return Response(_data)


class TestResultFilterView(generics.GenericAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = TestResultDRPSerializer

    def get_queryset(self):
        queryset = TestcaseExcelResult.get_unique_filters()
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            self.response_format["success"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = queryset
            self.response_format["message"] = "Success"
            return Response(self.response_format, status=status.HTTP_200_OK)
        if not queryset:
            self.response_format["success"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Error"
            return Response(self.response_format, status=status.HTTP_200_OK)
        return Response(
            self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class NavBarFilter(generics.GenericAPIView):

    serializer_class = NavbarFilterSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    def get_queryset(self):
        queryset = Natco.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        if serializer.data:
            self.response_format["success"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = serializer.data
            self.response_format["message"] = "Success"
            return Response(self.response_format, status=status.HTTP_200_OK)
        if not serializer.data:
            self.response_format["success"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Error"
            return Response(self.response_format, status=status.HTTP_200_OK)
        return Response(
            self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class TestCaseDetailReport(generics.GenericAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = NatcoGraphAPISerializer

    def get_queryset(self):
        queryset = TestcaseExcelResult.objects.filter(
            testcase=self.request.GET.get("testcase")
        ).values("natco")
        natco = self.request.GET.get("natco")
        match self.kwargs.get("type"):
            case "load_time":
                if natco is not None:
                    queryset = queryset.filter(
                        natco__contains=self.request.GET.get("natco")
                    )
                queryset = queryset.annotate(avg_load_time=Avg("load_time"))
            case "cpu_load":
                if natco is not None:
                    queryset = queryset.filter(
                        natco__contains=self.request.GET.get("natco")
                    )
                queryset = queryset.annotate(avg_load_time=Avg("load_time"))
            case "ram_load":
                if natco is not None:
                    queryset = queryset.filter(
                        natco__contains=self.request.GET.get("natco")
                    )
                queryset = queryset.annotate(avg_load_time=Avg("load_time"))
            case _:
                raise ValueError
        return queryset

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        if serializer.data:
            self.response_format["success"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = serializer.data
            self.response_format["message"] = "Success"
            return Response(self.response_format, status=status.HTTP_200_OK)
        if not serializer.data:
            self.response_format["success"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Error"
            return Response(self.response_format, status=status.HTTP_200_OK)
        return Response(
            self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class TestCaseReportView(generics.GenericAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = DistinctTestResultSerializer

    def get_queryset(self):
        results = TestcaseExcelResult.objects.values("testcase", "natco").annotate(
            min_cpu=Min("cpu_usage"),
            min_ram=Min("ram_usage"),
            min_time=Min("load_time"),
        )
        # Now, let's filter the results to get the distinct testcase and distinct natco with the minimum values
        distinct_results = []
        for result in results:
            distinct_result = TestcaseExcelResult.objects.filter(
                testcase=result["testcase"],
                natco=result["natco"],
                cpu_usage=result["min_cpu"],
                ram_usage=result["min_ram"],
                load_time=result["min_time"],
            ).first()
            if distinct_result:
                distinct_results.append(distinct_result)
        return distinct_results

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        if serializer.data:
            self.response_format["success"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = serializer.data
            self.response_format["message"] = "Success"
            return Response(self.response_format, status=status.HTTP_200_OK)
        if not serializer.data:
            self.response_format["success"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Error"
            return Response(self.response_format, status=status.HTTP_200_OK)
        return Response(
            self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ReportView(generics.GenericAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = GraphReportSerializer

    def get_queryset(self):
        queryset = TestReport.objects.values('testcase__test_name', 'node').annotate(
                                                                              cpu=Min("cpu_usage_percentile"),
                                                                              loadtime=Min("loadtime_percentile"),
                                                                              ram=Min("ram_usage_percentile")
                                                                            )
        return queryset

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        _data = defaultdict(lambda: defaultdict(list))
        for item in serializer.data:
            cpu_data = {
                'natco': item['natco'],
                'buildname': item['natco_version'],
                'value': item['cpu']
            }
            ram_data = {
                'natco': item['natco'],
                'buildname': item['natco_version'],
                'value': item['ram']
            }
            load_data = {
                'natco': item['natco'],
                'buildname': item['natco_version'],
                'value': item['loadtime']
            }
            _data[item['testcase']]['cpu'].append(cpu_data)
            _data[item['testcase']]['ram'].append(ram_data)
            _data[item['testcase']]['loadtime'].append(load_data)
        final_output = []
        for testcase_name, metrics in _data.items():
            final_output.append({
                'testcaseName': testcase_name,
                'cpu': metrics['cpu'],
                'RAM': metrics['ram'],
                'Load': metrics['loadtime']
            })
        if final_output:
            self.response_format["success"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = final_output
            self.response_format["message"] = "Success"
            return Response(self.response_format, status=status.HTTP_200_OK)
        if not final_output:
            self.response_format["success"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Error"
            return Response(self.response_format, status=status.HTTP_200_OK)
        return Response(
            self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class TestReportGraphView(generics.GenericAPIView):

    def get_queryset(self):
        queryset = TestReport.objects.values('testcase__test_name', 'node').annotate(
                                                                              cpu=Min("cpu_usage_percentile"),
                                                                              loadtime=Min("loadtime_percentile"),
                                                                              ram=Min("ram_usage_percentile")
                                                                            )
        return queryset


class TestView(APIView):

    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    def get_query_dict(self):
        _dict = {}
        testcase = TestcaseExcelResult.objects.distinct("testcase", "natco")
        for t in testcase:
            try:
                test = TestcaseExcelResult.objects.filter(testcase=t)
                for i in test:
                    if i.testcase not in _dict:
                        _dict[t.testcase] = {
                            i.natco: {
                                "load_time": i.load_time,
                                "cpu_usage": i.cpu_usage,
                                "ram_usage": i.ram_usage,
                            }
                        }
                    else:
                        x = _dict[t.testcase]
                        x[i.natco] = {
                            "load_time": i.load_time,
                            "cpu_usage": i.cpu_usage,
                            "ram_usage": i.ram_usage,
                        }
            except TestcaseExcelResult.DoesNotExist:
                _dict[t] = False
        return _dict

    def get(self, request, *args, **kwargs):
        queryset = self.get_query_dict()
        if queryset:
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = queryset
            self.response_format["message"] = "Success"
        else:
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "No Data"
        return Response(self.response_format)


class ExcelUploadView(generics.GenericAPIView):

    serializer_class = ExcelSerializer

    def post(self, request, *args, **kwargs):
        try:
            kwargs_splitted = kwargs.get("path").split("/")
            method = request.FILES.get("file")
            instance = None
            if kwargs_splitted[0] == "report":
                instance = ReportExcel(file=method).import_data()
            elif kwargs_splitted[0] == 'self':
                instance = UserStoryExcel(file=method).import_data()
            elif kwargs_splitted[0] == 'k':
                instance = TestcaseMetaExcel(file=method).import_data()
            elif kwargs_splitted[0] == 'demo':
                instance = TestCaseDemoExcel(file=method).import_data()
            return Response(instance)
        except Exception as e:
            return Response(str(e))


class DemoView(generics.GenericAPIView):

    serializer_class = TestCaseSerializer

    def get_queryset(self):
        queryset = TestCaseModel.objects.prefetch_related('test_steps').get(id=13005)
        print(len(queryset.test_steps.all()))
        return queryset

    def get(self, request):
        serializer = self.get_serializer(self.get_queryset())
        return Response(serializer.data)


@extend_schema(
    summary="Retrieve History of Test Case Changes",
    description=(
        "This endpoint retrieves the change history for a specific test case identified by its ID.\n\n"
        "The response contains a list of historical entries, "
        "with each entry showing the changes made to the test case.\n"
        "Only entries with a non-null `changed_to` field are included in the response."
    ),
    tags=["TestCase Module APIS"]
)
class HistoryView(generics.GenericAPIView):

    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = HistorySerializer

    def get_queryset(self):
        queryset = TestCaseModel.objects.get(id=self.kwargs.get('id'))
        return queryset.history.filter(history_type="~")

    def get(self, request, *args, **kwargs):
        print(self.get_queryset())
        serializer = self.get_serializer(self.get_queryset(), many=True)

        self.response_format["status"] = True
        self.response_format["status_code"] = status.HTTP_200_OK
        self.response_format["data"] = serializer.data
        self.response_format["message"] = "Success"
        return Response(self.response_format, status=status.HTTP_200_OK)



@extend_schema(
    summary="Retrieve and Create Script Issues",
    description=(
        "This endpoint allows you to retrieve all script issues associated with a "
        "specific test case identified by its ID.\n\n"
        "You can also create a new script issue by providing the required details in the request body."
    ),
    tags=["TestCase Module APIS"]
)
class ScriptIssueView(generics.ListCreateAPIView):

    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = ScriptIssueSerializer

    def get_queryset(self):
        queryset = TestCaseModel.objects.prefetch_related('issues').get(id=self.kwargs.get("id"))
        return queryset.issues.all()

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        if serializer.data:
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = serializer.data
            self.response_format["message"] = "Success"
        else:
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "No Data"
        return Response(self.response_format)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.create(serializer.validated_data, id=self.kwargs.get('id', None))
                self.response_format["status"] = True
                self.response_format["status_code"] = status.HTTP_200_OK
                self.response_format["data"] = serializer.data
                self.response_format["message"] = "Success"
                return Response(self.response_format)
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_202_ACCEPTED
            self.response_format["data"] = "Created"
            self.response_format["message"] = serializer.errors
            return Response(self.response_format)
        except Exception as e:
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = "Created"
            self.response_format["message"] = "Success"
            return Response(self.response_format)


@extend_schema(
    summary="Retrieve, Update, and Delete Script Issue",
    description=(
        "This endpoint allows you to retrieve, update, or delete a specific script issue identified by its ID.\n\n"
        "You can update the script issue by providing the required fields in the request body. "
        "To delete a script issue, simply send a DELETE request to this endpoint."
    ),
    tags=["TestCase Module APIS"]
)
class ScriptIssueDetailView(generics.GenericAPIView):

    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = ScriptIssueSerializer

    def get_queryset(self):
        queryset = ScriptIssue.objects.get(id=self.kwargs.get("id"))
        return queryset

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset())
        if serializer.data:
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = serializer.data
            self.response_format["message"] = "Success"
        else:
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "No Data"
        return Response(self.response_format)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_queryset(), data=request.data)
        if serializer.is_valid():
            serializer.save()
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = serializer.data
            self.response_format["message"] = "Success"
            return Response(self.response_format)
        self.response_format["status"] = False
        self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
        self.response_format["message"] = "No Data"
        return Response(self.response_format)


@extend_schema(
    summary="List and Create Comments",
    description=(
        "This endpoint allows users to retrieve a list all the comments of a Script Issue and create new comments"
        " for a Script Issue\n\n"
        "To create a new comment, provide the required fields in the request body, such as 'text' and 'author'."
    ),
    tags=["TestCase Module APIS"]
)
class CommentsView(generics.ListCreateAPIView):

    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = Comment.objects.filter(object_id=self.kwargs['id'])
        return queryset

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        if serializer.data:
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = serializer.data
            self.response_format["message"] = "Success"
        else:
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "No Data"
        return Response(self.response_format)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.create(serializer.validated_data)
                self.response_format["status"] = True
                self.response_format["status_code"] = status.HTTP_200_OK
                self.response_format["data"] = "Created"
                self.response_format["message"] = "Success"
                return Response(self.response_format)
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format['data'] = serializer.errors
            self.response_format["message"] = "No Data"
            return Response(self.response_format)
        except Exception as e:
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format['data'] = e
            self.response_format["message"] = "No Data"
            return Response(self.response_format)


@extend_schema(
    summary="Retrieve and Edit Comment",
    description=(
        "This endpoint allows users to retrieve a specific comment by its ID and update the comment's text.\n\n"
        "To update a comment, provide the new text in the request body."
    ),
    tags=["TestCase Module APIS"]
)
class CommentEditView(generics.GenericAPIView):

    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = Comment.objects.get(id=self.kwargs['pk'])
        return queryset

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset())
        if serializer:
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = serializer.data
            self.response_format["message"] = "Success"
        else:
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "No Data"
        return Response(self.response_format)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_queryset(), data=request.data)
        if serializer.is_valid():
            serializer.save()
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = serializer.data
            self.response_format["message"] = "Success"
            return Response(self.response_format)
        self.response_format["status"] = False
        self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
        self.response_format["message"] = "No Data"
        return Response(self.response_format)


class TestcaseScriptView(generics.GenericAPIView):

    serializer_class = TestcaseScriptSerializer

    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    def get_queryset(self):
        queryset = TestCaseScript.objects.filter(testcase=self.kwargs['pk'])
        return queryset

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                self.response_format["status"] = True
                self.response_format["status_code"] = status.HTTP_201_CREATED
                self.response_format["data"] = "Created"
                self.response_format["message"] = "Script Created"
                return Response(self.response_format, status=status.HTTP_200_OK)
            else:
                self.response_format["status"] = False
                self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
                self.response_format["data"] = serializer.errors
                self.response_format["message"] = "Error While Creating a New Script"
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.response_format["data"] = "Error"
            self.response_format["message"] = str(e)
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


class TestCaseScriptList(generics.ListAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = TestcaseScriptSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = TestCaseScript.objects.filter(testcase=self.kwargs['pk'])
        return queryset

    def get_serializer_context(self):
        return {
            "request": self.request
        }


class TestcaseScriptDetailView(generics.GenericAPIView):

    serializer_class = TestcaseScriptSerializer

    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    def get_queryset(self):
        queryset = TestCaseScript.objects.get(id=self.kwargs['pk'])
        return queryset

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset())
        if serializer.data:
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = serializer.data
            self.response_format["message"] = "Script Details"
            return Response(self.response_format, status=status.HTTP_200_OK)
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_queryset(), data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                self.response_format["status"] = True
                self.response_format["status_code"] = status.HTTP_200_OK
                self.response_format["data"] = serializer.data
                return Response(self.response_format, status=status.HTTP_200_OK)
            else:
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.response_format["data"] = "Error"
            self.response_format["message"] = str(e)
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_queryset(), data=request.data, partial=True)
        try:
            if serializer.is_valid():
                serializer.save()
                self.response_format["status"] = True
                self.response_format["status_code"] = status.HTTP_200_OK
                self.response_format["data"] = serializer.data
                return Response(self.response_format, status=status.HTTP_200_OK)
            else:
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.response_format["data"] = "Error"
            self.response_format["message"] = str(e)
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


class TestScoreView(generics.GenericAPIView):

    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = TestMetaDataSerializer
    ordering_fields = ['get_testscore']

    def get_queryset(self):
        queryset = TestCaseMetaData.objects.select_related('testcase').filter(testcase__project__project_key='dt')
        return queryset

    def get(self, request, *args, **kwargs):
        res = self.get_serializer(self.get_queryset(), many=True)
        if not res.data:
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_404_NOT_FOUND
            self.response_format["data"] = "Not Found"
            self.response_format["message"] = "No TestCase Meta Data for this Project"
            return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)
        else:
            sorted_testcase = sorted(res.data, key=lambda k: k['get_testscore'], reverse=True)
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = sorted_testcase
            self.response_format["message"] = "Success"
            return Response(sorted_testcase, status=status.HTTP_200_OK)


class TestCasePlanningView(generics.ListCreateAPIView):

    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    def get_queryset(self):
        queryset = TestPlanning.objects.filter(project=self.kwargs['project'])
        return queryset

    serializer_class = TestPlanningSerializer
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.response_format["status"] = True
        self.response_format["status_code"] = status.HTTP_200_OK
        self.response_format["data"] = response.data
        self.response_format["message"] = "Test Planning"
        return Response(self.response_format, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        self.response_format["status"] = True
        self.response_format["status_code"] = status.HTTP_200_OK
        self.response_format["data"] = response.data
        self.response_format["message"] = "Test Planning Created Successfully"
        return Response(self.response_format, status=status.HTTP_200_OK)

