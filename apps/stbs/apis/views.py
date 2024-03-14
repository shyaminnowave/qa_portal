from rest_framework import generics 
from rest_framework.viewsets import ModelViewSet
from apps.stbs.models import Language
from apps.stbs.apis.serializers import LanguageSerializer


class LanguageViewset(ModelViewSet):
    
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
