from rest_framework import generics 
from rest_framework.viewsets import ModelViewSet
from apps.stbs.models import Language, STBManufacture, Natco, NactoManufactureLanguage
from apps.stbs.apis.serializers import LanguageSerializer, STBManufactureSerializer, NactoSerializer, \
    NatcoLanguageSerializer, NatcoOptionSerializer, LanguageOptionSerializer, DeviceOptionSerializer
from apps.testcase_app.pagination import CustomPagination
from apps.stbs.mixins import OptionMixin
from apps.stbs.permissions import LangaugeOptionPermission, NatcoOptionPermission, DeviceOptionPermission, \
        AdminPermission, LanguagePermission
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiSchemaBase
from drf_spectacular.openapi import OpenApiTypes, OpenApiExample


class LanguageViewset(ModelViewSet):
    # permission_classes = [LanguagePermission]
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    pagination_class = CustomPagination

    @extend_schema(
        request=LanguageSerializer,
        responses={201, LanguageSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class STBManufactureViewSet(ModelViewSet):
    # permission_classes = [AdminPermission]
    queryset = STBManufacture.objects.all()
    serializer_class = STBManufactureSerializer
    pagination_class = CustomPagination


class NatcoViewSet(ModelViewSet):
    # permission_classes = [AdminPermission]
    queryset = Natco.objects.all()
    serializer_class = NactoSerializer
    pagination_class = CustomPagination


class NatcoLanguageViewSet(ModelViewSet):
    # permission_classes = [AdminPermission]
    queryset = NactoManufactureLanguage.objects.all()
    serializer_class = NatcoLanguageSerializer
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        return super(NatcoLanguageViewSet, self).create()


class NatcoOptionView(OptionMixin, generics.GenericAPIView):
    # permission_classes = [NatcoOptionPermission]
    queryset = Natco.objects.all()
    serializer_class = NatcoOptionSerializer


class LanguageOptionView(OptionMixin, generics.GenericAPIView):
    # permission_classes = [LangaugeOptionPermission]
    queryset = Language.objects.all()
    serializer_class = LanguageOptionSerializer


class DeviceOptionView(OptionMixin, generics.GenericAPIView):
    # permission_classes = [DeviceOptionPermission]
    queryset = STBManufacture.objects.all()
    serializer_class = DeviceOptionSerializer


