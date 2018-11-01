from http import HTTPStatus

from django.http import JsonResponse

from django.views import View
from django.views.generic.list import MultipleObjectMixin

from news.models import NewsModel
from news.serializers import NewsSerializer


class ApiErrorResponse(JsonResponse):
    """Api error response """

    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, error, **kwargs):
        data = {'error': error}
        super().__init__(data, **kwargs)


class ApiResponse(JsonResponse):
    """Api response"""

    def __init__(self, objects, count, **kwargs):
        data = {
            'count': count,
            'objects': objects
        }
        super().__init__(data, **kwargs)


class BaseAPIView(View, MultipleObjectMixin):
    """Base class for api views

    It uses MultipleObjectMixin api for work
    """

    serializer = None
    paginate_by = 100

    def get(self, request):
        """Make Json response for api requests

        Parameters
        ----------
        request

        Returns
        -------
        JsonResponse
        """
        try:
            qs = self.get_queryset()
            paginator, page, queryset, is_paginated = self.paginate_queryset(qs, self.paginate_by)
            serializer = self.serializer()
            resp = ApiResponse([serializer.serialize(o) for o in page.object_list], paginator.count)
        except Exception as e:
            resp = ApiErrorResponse(str(e))

        return resp


class NewsAPIView(BaseAPIView):
    """News api view"""

    serializer = NewsSerializer
    model = NewsModel
    ordering = '-published_at'
