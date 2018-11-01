from django.urls import path

from news.views import NewsListView
from news.views_api import NewsAPIView

api_urls = [
    path('news/', NewsAPIView.as_view(), name='news')
]

app_name = 'news'
urlpatterns = [
    path('', NewsListView.as_view(), name='news-list'),
    path('<int:page>/', NewsListView.as_view(), name='news-list')
]