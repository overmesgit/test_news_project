import json

from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus

from django.utils.timezone import now

from news.models import NewsSourceModel, NewsModel
from news.views_api import NewsAPIView


class ApiTestCase(TestCase):

    def test_empty_db(self):
        resp = self.client.get(reverse('api:news'))
        self.assertEqual(HTTPStatus.OK, resp.status_code, resp.content)

        resp_data = json.loads(resp.content)
        self.assertEqual(0, resp_data['count'])
        self.assertEqual([], resp_data['objects'])

    def test_validate_params(self):
        invalid_pages = ['asdf', 0, -1]
        for page in invalid_pages:
            with self.subTest(page):
                resp = self.client.get(reverse('api:news'), data={'page': page})
                self.assertEqual(HTTPStatus.BAD_REQUEST, resp.status_code, resp.content)

                resp_data = json.loads(resp.content)
                self.assertIn('page', resp_data['error'].lower())

    def test_pagination(self):
        source = NewsSourceModel.objects.create(domain='news.com')

        news_count = 340
        news_to_create = []
        for i in range(news_count):
            n = NewsModel(source=source, url=f'http://some.domain.com/path/{i}', title=f'some title {i}',
                          published_at=now())
            news_to_create.append(n)

        NewsModel.objects.bulk_create(news_to_create)

        resp = self.client.get(reverse('api:news'))
        self.assertEqual(HTTPStatus.OK, resp.status_code, resp.content)

        resp_data = json.loads(resp.content)
        self.assertEqual(news_count, resp_data['count'])
        self.assertEqual(100, len(resp_data['objects']))

        # ordering
        qs = NewsModel.objects.order_by('-published_at')[:100].values_list('id', flat=True)
        self.assertSequenceEqual(qs, [o['id'] for o in resp_data['objects']])

        # last page not full
        resp = self.client.get(reverse('api:news'), data={'page': news_count//NewsAPIView.paginate_by+1})
        self.assertEqual(HTTPStatus.OK, resp.status_code, resp.content)

        resp_data = json.loads(resp.content)
        self.assertEqual(news_count, resp_data['count'])
        self.assertEqual(news_count % NewsAPIView.paginate_by, len(resp_data['objects']))
