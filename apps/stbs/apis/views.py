from rest_framework import generics 
from rest_framework.viewsets import ModelViewSet
from apps.stbs.models import Language, STBManufacture, Natco, NactoManufactureLanguage
from apps.stbs.apis.serializers import LanguageSerializer, STBManufactureSerializer, NactoSerializer, NatcoLanguageSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.testcase_app.pagination import CustomPagination


@swagger_auto_schema(
    operation_description="Test Description"
)
class LanguageViewset(ModelViewSet):
    
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    pagination_class = CustomPagination


class STBManufactureViewset(ModelViewSet):

    queryset = STBManufacture.objects.all()
    serializer_class = STBManufactureSerializer
    pagination_class = CustomPagination


class NatcoViewSet(ModelViewSet):

    queryset = Natco.objects.all()
    serializer_class = NactoSerializer
    pagination_class = CustomPagination


class NatcoLanguageViewSet(ModelViewSet):

    queryset = NactoManufactureLanguage.objects.all()
    serializer_class = NatcoLanguageSerializer
    pagination_class = CustomPagination