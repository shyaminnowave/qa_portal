from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import generics
from analytiqa.helpers.renders import ResponseInfo
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status


class ERROR404View(generics.GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, *args, **kwargs):
        # Log or print for debugging purposes
        print('404 - Invalid URL accessed')

        # Return the response with a 404 status and an HTML template
        return Response(
            {'message': "Invalid URL", 'status_code': status.HTTP_404_NOT_FOUND},
            template_name='error404.html',
            status=status.HTTP_404_NOT_FOUND
        )


class ERROR505View(generics.GenericAPIView):

    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, *args, **kwargs):
        pass


error404 = ERROR404View.as_view()

