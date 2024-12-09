from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from analytiqa.helpers.renders import ResponseInfo
from rest_framework import status
from rest_framework.views import Response

class CustomJWTAuthentication(JWTAuthentication):

    def __init__(self, *args, **kwargs):
        print('Testing')
        self.response_format = {
            "status": False,
            "status_code": None,
            "message": None,
            "data": None
        }
        super().__init__(*args, **kwargs)

    def authenticate(self, request):
        try:
            # Call the parent class's authenticate method
            return super().authenticate(request)
        except AuthenticationFailed as e:
            raise AuthenticationFailed(detail="Authorization header must contain two space-delimited values")
        except TokenError as e:
            raise AuthenticationFailed(detail="Invalid token. Please provide a valid token.")
        except InvalidToken as e:
            raise AuthenticationFailed(detail="Token invalid. Please provide a valid token.")
        except Exception as e:
            raise AuthenticationFailed(detail="An unexpected error occurred during authentication.")