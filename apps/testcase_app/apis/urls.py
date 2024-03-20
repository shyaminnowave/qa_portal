from django.urls import path
from apps.testcase_app.apis import views


urlpatterns = [
    path('test-case/', views.TestCaseListView.as_view()),
    path('create/test-case/', views.TestCaseView.as_view()),
    path('test-case/<int:jira_id>/', views.TestCaseDetailView.as_view())
]
