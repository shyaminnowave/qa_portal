from django.urls import path
from apps.testcase_app.apis import views


urlpatterns = [
    path('list/test-case/', views.TestCaseListView.as_view())
]
