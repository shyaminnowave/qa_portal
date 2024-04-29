from rest_framework.views import Response
from rest_framework import generics
from apps.account.models import Account
from apps.account.apis.serializers import AccountSerializer, LoginSerializer, ProfileSerializer, UserListSerializer, \
                                PermissionSerializer, GroupListSerializer, GroupSerializer, UserSerializer
from django.contrib.auth import authenticate
from rest_framework import status
from apps.account.utils import get_token_for_user
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.account.signals import user_token_login, user_token_logout
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view
from drf_spectacular.types import OpenApiTypes
from apps.testcase_app.apis.views import CustomPagination
from django.contrib.auth.models import Group, Permission
from apps.account.permissions import AdminUserPermission, DjangoModelPermissions, UserPermission, \
    GroupCreatePermission, DjangoObjectPermissions
from rest_framework.permissions import IsAuthenticated


class AccountCreateView(generics.CreateAPIView):

    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            return Response({"success": True, 'data': "User Creation Successfull"}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "error": "User Creation Failed"}, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(generics.GenericAPIView):
    
    queryset = Account.objects.all()
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_cred = self._perform_login(request, email, password)
            if user_cred is not None:
                response = Response({'success': True, 'message': 'Login Successfull', 'data': user_cred},
                                    status=status.HTTP_200_OK)
                return response
        return Response({'success': False, 'error': "Please Check the login Creditionals"},
                        status=status.HTTP_404_NOT_FOUND)
    
    def _perform_login(self, request, email, password):
        user = authenticate(email=email, password=password)
        if user is not None:
            user_token_login.send(sender=user, user=user, request=request)
            token = get_token_for_user(user)
            return {
                'access': token['access'],
                'refresh': token['refresh'],
                'email': user.email,
                'username': user.username
            }
        return None
    

class LogoutView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            if request.user.is_authenticated and isinstance(request.user, Account):
                user_token_logout.send(sender=request.user.__class__, user=request.user, request=request)
                token.blacklist()
                return Response({"success": True, "data": "Logout Successfull"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"success": False, "data": "Error"}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.GenericAPIView):

    permission_classes = [UserPermission]

    queryset = Account.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'username'

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response({"success": True, "data": serializer.data})

    def patch(self, request, *args, **kwargs):
        """ Pending """
        pass


class UserListView(generics.ListAPIView):

    permission_classes = [UserPermission]

    queryset = Account.objects.all()
    serializer_class = UserListSerializer
    pagination_class = CustomPagination


class UserUpdateGroup(generics.RetrieveUpdateAPIView):

    permission_classes = [AdminUserPermission]

    queryset = Account.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'


class PermissionListView(generics.ListAPIView):

    permission_classes = [AdminUserPermission]
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class GroupView(generics.ListAPIView):

    permission_classes = [UserPermission]
    queryset = Group.objects.all()
    serializer_class = GroupListSerializer

    def get_serializer_context(self):
        return {"request": self.request}


class GroupCreateView(generics.CreateAPIView):

    permission_classes = [DjangoModelPermissions]

    queryset = Group.objects.all()
    serializer_class = GroupListSerializer

    def post(self, request, *args, **kwargs):
        response = super(GroupCreateView, self).post(request, *args, **kwargs)
        return Response({'success': True, 'data': response.data})


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [DjangoObjectPermissions]

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    lookup_field = 'pk'


