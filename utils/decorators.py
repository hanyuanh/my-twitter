from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def required_params(request_attr='query_params', params=None):
    """
    When @required_params(params=['some_param']) is being used,
    the required_params method should return a decorator, whose parameters is
    the method view_func that is being wrapped by @required_params
    """

    # From a coding habit standpoint, the param list of the method cannot be a
    # mutable param
    if params is None:
        params = []

    def decorator(view_func):
        """
        decorator method parses the params in view_func and passes to
        _wrapped_view. Here instance param is self in view_func
        """
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            data = getattr(request, request_attr)
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    'message': u'missing {} in request'.format(params_str),
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)
            # After checking, call view_func wrapped by @required_params
            return view_func(instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator