from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from apps.core.models import Project, ProjectIntegration
from apps.core.utils import get_issues
from apps.account.models import ThirdPartyIntegrationTable
from apps.testcases.apis.views import CustomPagination
from apps.core.apis.serializers import ProjectSerializer, ProjectIntegrationSerializer
from analytiqa.helpers import custom_generics as cgenerics
from analytiqa.helpers.renders import ResponseInfo
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.account.utils import new_get_project
from rest_framework.permissions import IsAuthenticated

class IssuesAPIView(generics.ListAPIView):

    pagination_class = CustomPagination
    serializer_class = None

    def get(self, request, *args, **kwargs):
        project = self.kwargs.get('project')
        api_token = ProjectIntegration.objects.filter(key=project).first()
        _data = get_issues(data=api_token, project=project, startAT=request.GET.get('startsAT', 0),
                           limit=self.request.GET.get('maxResults', 50))
        page = self.paginate_queryset(_data)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(_data)


class ProjectAPIView(generics.ListCreateAPIView):

    def __init__(self, *args, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(*args, **kwargs)

    authentication_classes = (JWTAuthentication,)
    # permission_classes = [IsAuthenticated,]

    pagination_class = CustomPagination
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = Project.objects.filter(account=self.request.user)
        return queryset

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = response.data
            self.response_format["message"] = "Project successfully retrieved"
        else:
            self.response_format["status"] = False
            self.response_format["status_code"] = response.status_code
            self.response_format["data"] = response.error
            self.response_format["message"] = "Error retrieving project"
            return Response(self.response_format, status=response.status_code)
        return Response(self.response_format, status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == status.HTTP_201_CREATED:
                self.response_format["status"] = True
                self.response_format["status_code"] = status.HTTP_201_CREATED
                self.response_format["data"] = response.data
                self.response_format["message"] = "New Project created"
            else:
                self.response_format["status"] = False
                self.response_format["status_code"] = response.status_code
                self.response_format["data"] = "null"
                self.response_format["message"] = "Project Creation Failed"
                return Response(self.response_format, status=response.status_code)
            return Response(self.response_format, status.HTTP_201_CREATED)
        except Exception as e:
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["data"] = None
            self.response_format["message"] = str(e)
            return Response(self.response_format, status.HTTP_400_BAD_REQUEST)


class ProjectDetailAPIView(cgenerics.CustomRetrieveUpdateAPIView):
    
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    serializer_class = ProjectSerializer
    
    def get_object(self):
        queryset = get_object_or_404(Project, id=self.kwargs.get('pk', None))
        return queryset

    def put(self, request, *args, **kwargs):
        super().put(request, *args, **kwargs)
        self.response_format["message"] = "Project Updated Successfully"
        return Response(self.response_format, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        super().patch(request, *args, **kwargs)
        self.response_format["message"] = "Project Updated Successfully"
        return Response(self.response_format, status=status.HTTP_200_OK)


class ProjectIntegrateDetailView(generics.GenericAPIView):

    def __init__(self, *args, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(*args, **kwargs)

    serializer_class = ProjectIntegrationSerializer

    def get_queryset(self):
        try:
            queryset = ProjectIntegration.objects.get(id=self.kwargs.get('pk', None), is_active=True)
            return queryset
        except Exception as e:
            return None

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset is None:
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_404_NOT_FOUND
            self.response_format["data"] = None
            self.response_format["message"] = "No Data Found"
            return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = self.get_serializer(queryset)
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = serializer.data
            self.response_format["message"] = "Success"
        return Response(self.response_format, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset is None:
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_404_NOT_FOUND
            self.response_format["data"] = None
            self.response_format["message"] = "No Data Found"
            return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = self.get_serializer(instance=queryset, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                self.response_format["status"] = True
                self.response_format["status_code"] = status.HTTP_200_OK
                self.response_format["data"] = serializer.data
                self.response_format["message"] = "Project Key Updated Successfully"
            return Response(self.response_format, status=status.HTTP_200_OK)


class ProjectIntegrationCreateView(generics.GenericAPIView):

    def __init__(self, *args, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(*args, **kwargs)

    serializer_class = ProjectIntegrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            _data = new_get_project(request.data)
            combined_data = serializer.data.copy()
            combined_data['project'] = _data
            self.response_format["status"] = True
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = combined_data
            self.response_format["message"] = "Project Integration Successfully"
        else:
            self.response_format["status"] = False
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["data"] = serializer.errors
            self.response_format["message"] = "Error"
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.response_format, status=status.HTTP_200_OK)