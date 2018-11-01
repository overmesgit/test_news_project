import json
from http import HTTPStatus

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.timezone import now

from news.models import NewsSourceModel, NewsModel


class MainNewsPage(TestCase):
    maxDiff = None

    def setUp(self):
        source = NewsSourceModel.objects.create(domain='news.com')

        self.news_count = 340
        news_to_create = []
        for i in range(self.news_count):
            n = NewsModel(source=source, url=f'http://some.domain.com/path/{i}', title=f'some title {i}',
                          published_at=now())
            news_to_create.append(n)

        NewsModel.objects.bulk_create(news_to_create)

    def test_main_page(self):
        resp = self.client.get(reverse('news:news-list'))
        self.assertEqual(HTTPStatus.OK, resp.status_code, resp.content)

        qs = NewsModel.objects.order_by('-published_at')[0:20]
        self.assertQuerysetEqual(qs, list(map(repr, resp.context['page_obj'].object_list)))

        # First page
        resp = self.client.get(reverse('news:news-list', kwargs={'page': 1}))
        self.assertEqual(HTTPStatus.OK, resp.status_code, resp.content)

        qs = NewsModel.objects.order_by('-published_at')[0:20]
        self.assertQuerysetEqual(qs, list(map(repr, resp.context['page_obj'].object_list)))

        # 3 page
        resp = self.client.get(reverse('news:news-list', kwargs={'page': 3}))
        self.assertEqual(HTTPStatus.OK, resp.status_code, resp.content)

        qs = NewsModel.objects.order_by('-published_at')[40:60]
        self.assertQuerysetEqual(qs, list(map(repr, resp.context['page_obj'].object_list)))

        # wrong pages
        resp = self.client.get(reverse('news:news-list') + 'asdf/')
        self.assertEqual(HTTPStatus.NOT_FOUND, resp.status_code, resp.content)

        resp = self.client.get(reverse('news:news-list') + '-123/')
        self.assertEqual(HTTPStatus.NOT_FOUND, resp.status_code, resp.content)

    @override_settings(IP_REQUESTS_IN_HOUR_LIMIT=5)
    def test_throttling(self):
        cache.clear()
        for i in range(5):
            resp = self.client.get(reverse('api:news'))
            self.assertEqual(HTTPStatus.OK, resp.status_code)

        resp = self.client.get(reverse('api:news'))
        self.assertEqual(HTTPStatus.TOO_MANY_REQUESTS, resp.status_code)
        self.assertIn('error', json.loads(resp.content))

        resp = self.client.get(reverse('news:news-list'))
        self.assertEqual(HTTPStatus.TOO_MANY_REQUESTS, resp.status_code)