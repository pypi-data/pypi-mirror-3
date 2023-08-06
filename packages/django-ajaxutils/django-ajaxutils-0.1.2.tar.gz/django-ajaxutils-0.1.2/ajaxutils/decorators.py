"""
syntactic sugar for Ajax requests in django
"""

from decorator import decorator

try:
    import simplejson as json
except ImportError:
    import json

from django.http import HttpResponse


class JsonResponse(HttpResponse):
    """
    HttpResponse descendant, which return response with ``application/json`` mimetype.
    """
    def __init__(self, data, status=200):
        super(JsonResponse, self).__init__(
            content=json.dumps(data),
            mimetype='application/json', status=status
        )


def ajax(login_required=False, require_GET=False, require_POST=False,
         require=None):
    """
    Usage:

    @ajax(login_required=True)
    def my_ajax_view(request):
        return {'count': 42}
    """
    def ajax(f, request, *args, **kwargs):
        """ wrapper function """
        if login_required:
            if not request.user.is_authenticated():
                return JsonResponse({
                    'status': 'error',
                    'error': 'Unauthorized',
                }, status=401)

        # check request method
        method = None
        if require_GET:
            method = "GET"
        if require_POST:
            method = "POST"
        if require:
            method = require
        if method and method != request.method:
            return JsonResponse({
                'status': 'error',
                'error': 'Method not allowed',
            }, status=405)

        response = f(request, *args, **kwargs)

        if isinstance(response, dict):
            return JsonResponse(response)
        else:
            return response

    return decorator(ajax)
