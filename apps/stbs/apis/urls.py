from django.urls import path
from rest_framework import routers
from apps.stbs.apis.views import LanguageViewset


routers = routers.SimpleRouter()
routers.register(r'language', LanguageViewset)

urlpatterns = [
    
]

urlpatterns += routers.urls