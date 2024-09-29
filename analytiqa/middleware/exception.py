from django.utils.deprecation import MiddlewareMixin
from more_itertools.more import raise_


class ExceptionMiddelware(MiddlewareMixin):

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def process_response(self, request, response):
        if response.status_code == 403:
            response.data = {"detail": "Custom Forbidden Message"}
        if response.status_code == 404:
            response.data = {"detail": "Not Found"}
        if response.status_code == 500:
            response.data = {"detail": "Internal Server Error"}
        raise BaseException(response.status_code)


