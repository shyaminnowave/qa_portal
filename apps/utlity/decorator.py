import functools
from rest_framework.views import Response
from rest_framework import status


def instance_check(kls, *check_params):
    def decor_func(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            _instance_params = {param: request.data.get(param) for param in check_params}
            _check = kls.objects.filter(**_instance_params).exists()
            if _check:
                return Response({})
            return func(request, *args, **kwargs)
        return wrapper
    return decor_func
