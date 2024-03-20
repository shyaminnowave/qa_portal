from django.urls import path
from rest_framework import routers
from apps.stbs.apis.views import LanguageViewset, STBManufactureViewset, NatcoViewSet, NatcoLanguageViewSet


routers = routers.SimpleRouter()
routers.register(r'language', LanguageViewset)
routers.register(r'stb-manufacture', STBManufactureViewset)
routers.register(r'natco', NatcoViewSet)
routers.register(r'nacto-language', NatcoLanguageViewSet)

urlpatterns = [
    
]

urlpatterns += routers.urls