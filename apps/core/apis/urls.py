from django.urls import path
from apps.core.apis.views import (IssuesAPIView, ProjectAPIView, ProjectDetailAPIView, ProjectIntegrateDetailView,
                                  ProjectIntegrationCreateView)


app_name = 'core'

urlpatterns = [
    path('<str:project>/issues/', IssuesAPIView.as_view(), name='issues'),
    path('project-list/', ProjectAPIView.as_view(), name='project-list'),
    path('project-details/<int:pk>/', ProjectDetailAPIView.as_view(), name='project-detail'),
    path('project-integration/', ProjectIntegrationCreateView.as_view(), name='project-integration'),
    path('project-integrate/detail/<int:pk>/', ProjectIntegrateDetailView.as_view(), name='project-integrate'),

]