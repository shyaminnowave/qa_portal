from django.urls import path
from apps.testcase_app.apis import views


app_name = 'testcases'

urlpatterns = [
    path('test-case/', views.TestCaseListView.as_view()),
    path('create/test-case/', views.TestCaseView.as_view()),
    path('test-case/<int:jira_id>/', views.TestCaseDetailView.as_view(), name='testcase-details'),
    path('test-case/status/', views.TestCaseStatusUpdateView.as_view()),
    path('test-case/natco/<int:jira_id>/', views.TestCaseNatcoView.as_view(), name='testcase-natco'),
    path('test-case/natco-list/', views.TestCaseNatcoList.as_view(), name='natco-list'),
    path('test-case/natco-list/<int:pk>/', views.TestCaseNatcoDetail.as_view(), name='natco-details'),
    path('bulk-upload/', views.GetTestCase.as_view()),
    path('perfomance-upload', views.GETPERFOMANCEEXCEL.as_view()),
    path('upload/test-result/', views.GetTestResult.as_view()),
    path('report-filter/', views.TestResultFilterView.as_view()),
    path('report-data/', views.TestCaseReportView.as_view())
]
