import logging
from http import HTTPStatus
from operator import itemgetter
from typing import Any, Optional, Dict, Tuple

import requests

from news.models import NewsSourceModel, NewsModel

logger = logging.getLogger()


class BaseScraper:
    """
    Abstract class for representing Scrapers

    To add new source implement create_source and create_news in subclass

    Attributes
    ----------
    main_url : str
        main url that will be used for downloading news

    Methods
    -------
    start(count: int=100, params: dict=None, path: str='')
        Download news from main_url
    create_source(data: Dict[str, Any])
        Validate fetched data, create and return NewsSourceModel
    create_news(sources_dict: Dict[str, NewsSourceModel], data: Dict[str, Any])
        Validate fetched data, create and return NewsModel
    """

    main_url: str = ''

    def __init__(self, api_key: str=''):
        """
        Parameters
        ----------
        api_key : str
            Api key for site
        """
        self.api_key = api_key

    def start(self, count: int=100, params: dict=None, path: str=''):
        """Download news from 'main_url + path?params' while they not end or count

        Parameters
        ----------
        count : int
            Downloading news until won't reach that number
        params: dict
            Special params that will be send to site
        path: str
            End point for downloading news

        Raises
        ------
        ValueError
            If site response not OK status code
        """
        full_url = f'{self.main_url}{path}'

        if params is None:
            params = {}

        downloaded_news = 0
        # we will receive proper value after first request
        total_count = 1
        page = 1
        while downloaded_news < count and downloaded_news < total_count:
            logger.info(f'Fetching page {page}')
            resp = requests.get(full_url, {**{'apiKey': self.api_key, 'page': page}, **params})

            if resp.status_code != HTTPStatus.OK:
                message = resp.json().get('message')
                raise ValueError(f'Error fetching data from {full_url}: {resp.reason} {message}')

            total_count, news_count = self._save_data(resp.json())
            downloaded_news += news_count
            page += 1

        return downloaded_news

    def create_source(self, data: Dict[str, Any]) -> Optional[NewsSourceModel]:
        """Create source model from site data"""
        raise NotImplementedError()

    def create_news(self, sources_dict: Dict[str, NewsSourceModel], data: Dict[str, Any]) -> Optional[NewsModel]:
        """Create news model from site data"""
        raise NotImplementedError()

    def _save_data(self, data: dict) -> Tuple[int, int]:
        """Receive one response from site and create sources and news

        Optimized for number of create db queries

        Parameters
        ----------
        data

        Returns
        -------
        tuple[int, int]
            return total available site results and currently receive news
        """
        # Looking for already existing sources
        existed_sources_dict, to_create_sources = self._get_existed_and_to_create_sources(data['articles'])
        NewsSourceModel.objects.bulk_create(to_create_sources)

        to_create_news = self._get_to_create_news(existed_sources_dict, data['articles'])
        NewsModel.objects.bulk_create(to_create_news)

        return int(data['totalResults']), len(data['articles'])

    def _get_existed_and_to_create_sources(self, articles: list) -> Tuple[dict, list]:
        """Find existed and new sources

        Optimized for number of check existence query

        Parameters
        ----------
        articles: list
            List with news data from site

        Returns
        -------
        dict
            Dict with source.pk as keys and source as value
        """
        key_source_dict = {}
        for news_data in articles:
            source = self.create_source(news_data)
            if source:
                key_source_dict[source.pk] = source

        existed_sources = NewsSourceModel.objects.filter(domain__in=key_source_dict.keys())
        existed_key_dict = {s.pk: s for s in existed_sources}

        to_create = [s for k, s in key_source_dict.items() if k not in existed_key_dict]
        sources_dict = {**key_source_dict, **existed_key_dict}
        return sources_dict, to_create

    def _get_to_create_news(self, sources_dict, articles: dict) -> list:
        """Find existed news and return list of NewsModel to create

        Parameters
        ----------
        sources_dict
        articles

        Returns
        -------
        list
            List of NewsModel that don't exist
        """
        key_news_dict = {}
        for news_data in articles:
            news = self.create_news(sources_dict, news_data)
            if news:
                key_news_dict[news.get_unique_key()] = news

        # For simplicity we receive news that have specific sources or paths or titles.
        # Because we use such union instead of ((source, path, title) or (...)) we can receive extra news
        # but this is not a big overhead
        _news_qs = NewsModel.objects.filter(source_id__in=sources_dict.keys())
        _news_qs = _news_qs.filter(normalized_path__in=map(itemgetter(1), key_news_dict.keys()))
        existed_news = _news_qs.filter(title__in=map(itemgetter(2), key_news_dict.keys()))

        existed_news_set = {n.get_unique_key() for n in existed_news}
        return [s for k, s in key_news_dict.items() if k not in existed_news_set]
