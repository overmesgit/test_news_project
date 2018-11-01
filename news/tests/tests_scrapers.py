from datetime import datetime

from django.test import TestCase
from pytz import utc

from news.models import NewsModel, NewsSourceModel
from news.scrapers.newsapi_org import NewsApiOrgScraper

sample_item = {
    "source": {"id": None, "name": "Makeuseof.com"},
    "author": "Ian Buckley",
    "title": "4 Reasons Why Python Isn’t the Programming Language for You",
    "description": "Python is one of the most popular programming languages of recent years.",
    "url": "https://www.makeuseof.com/tag/python-programming-language-downsides/",
    "urlToImage": "https://static.makeuseof.com/wp-content/uploads/2018/10/No-Pytho-994x400.jpg",
    "publishedAt": "2018-10-04T09:00:00Z",
    "content": "some content"
}
sample_data = {
    "status": "ok",
    "totalResults": 9121,
    "articles": [
        sample_item,
    ]
}


class FetchNewsTest(TestCase):
    # def test_fetch_news(self):
    #     from django.core.management import call_command
    #     call_command('fetch_news', apikey='', count=10)

    def test_save_news(self):
        total_res, news_count = NewsApiOrgScraper()._save_data(sample_data)

        self.assertEqual(sample_data['totalResults'], total_res)
        self.assertEqual(len(sample_data['articles']), news_count)

        self.assertEqual(1, NewsModel.objects.count())
        self.assertEqual(1, NewsSourceModel.objects.count())

        source = NewsSourceModel.objects.first()
        self.assertEqual('makeuseof.com', source.domain)

        field_answer = {
            'author': sample_item['author'],
            'title': sample_item['title'],
            'description': sample_item['description'],
            'url': sample_item['url'],
            'image_url': sample_item['urlToImage'],
            'published_at': datetime(2018, 10, 4, 9, tzinfo=utc),
            'content': sample_item['content']
        }

        saved_news = NewsModel.objects.first()
        for field, answer in field_answer.items():
            self.assertEqual(answer, getattr(saved_news, field))

        # try to save same data one more time
        NewsApiOrgScraper()._save_data(sample_data)
        self.assertEqual(1, NewsModel.objects.count())
        self.assertEqual(1, NewsSourceModel.objects.count())

    def test_minimal_set_of_fields(self):
        small_sample = {
            "source": {"id": None, "name": "Makeuseof.com"},
            "title": "4 Reasons Why Python Isn’t the Programming Language for You",
            "url": "https://www.makeuseof.com/tag/python-programming-language-downsides/",
            "publishedAt": "2018-10-04T09:00:00Z",
            "author": None,
            "description": None,
            "urlToImage": None,
            "content": None
        }

        sample_copy = sample_data.copy()
        sample_copy['articles'] = [small_sample]

        NewsApiOrgScraper()._save_data(sample_copy)
        self.assertEqual(1, NewsModel.objects.count())
        self.assertEqual(1, NewsSourceModel.objects.count())

    def test_field_validation(self):
        small_sample = {
            "source": {"id": None, "name": "Makeuseof.com"},
            "author": "Ian Buckley",
            "title": "999 Reasons Why Python is awesome",
            "description": "Python is one of the most popular programming languages of recent years.",
            "url": "https://www.makeuseof.com/tag/python-programming-language-downsides/",
            "urlToImage": "https://static.makeuseof.com/wp-content/uploads/2018/10/No-Pytho-994x400.jpg",
            "publishedAt": "2018-10-04T09:00:00Z",
            "content": "some content"
        }
        sample_copy = sample_data.copy()

        sample_copy['articles'] = [{**small_sample, **{'url': 'asdf'}}]
        NewsApiOrgScraper()._save_data(sample_copy)
        self.assertEqual(0, NewsModel.objects.count())
        self.assertEqual(0, NewsSourceModel.objects.count())

        sample_copy['articles'] = [{**small_sample, **{'publishedAt': 'asdf'}}]
        NewsApiOrgScraper()._save_data(sample_copy)
        self.assertEqual(0, NewsModel.objects.count())

        sample_copy['articles'] = [{**small_sample, **{'urlToImage': 'asdf'}}]
        NewsApiOrgScraper()._save_data(sample_copy)
        self.assertEqual(0, NewsModel.objects.count())
