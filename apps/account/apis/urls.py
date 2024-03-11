from django.urls import path
from apps.account.apis import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('create-account/', views.AccountCreateView.as_view(), name='create-user'), 
    path('login/', views.LoginView.as_view(), name='login')
]
