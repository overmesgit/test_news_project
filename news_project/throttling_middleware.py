from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse

from news.views_api import ApiErrorResponse


class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        addr = request.META['REMOTE_ADDR']

        request_in_last_our = cache.get(addr) or 0

        if request_in_last_our >= settings.IP_REQUESTS_IN_HOUR_LIMIT:
            if 'api/' in request.path:
                response = ApiErrorResponse('Too many request', status=HTTPStatus.TOO_MANY_REQUESTS)
            else:
                response = HttpResponse(b'Too many requests', status=HTTPStatus.TOO_MANY_REQUESTS)
        else:
            cache.set(addr, request_in_last_our + 1, 3600)
            response = self.get_response(request)

        return response
