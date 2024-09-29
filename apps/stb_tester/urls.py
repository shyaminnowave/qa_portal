from django.urls import path
from apps.stb_tester import views

app_name = 'stb-tester'

urlpatterns = [
    path('testcase/result/<int:id>/', views.StbTestCaseResult.as_view())
]
