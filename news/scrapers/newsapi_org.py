import logging
from typing import Optional, Any, Dict

from django import forms

from news.models import NewsSourceModel, NewsModel
from news.scrapers.base import BaseScraper
from news.utils.url_normalizer import get_normalized_domain_name

logger = logging.getLogger()


class OptionalValidateUniqueMixin:
    def __init__(self, *args, validate_unique=True, **kwargs):
        super().__init__(*args, **kwargs)

        # we will check it ourselves
        self.validate_unique_flag = validate_unique

    def validate_unique(self):
        if self.validate_unique_flag:
            super().validate_unique()


class NewsForm(OptionalValidateUniqueMixin, forms.ModelForm):
    """Model form to validate data from newsapi.org"""

    published_at = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%SZ'])

    class Meta:
        model = NewsModel
        fields = '__all__'


class NewsSourceForm(OptionalValidateUniqueMixin, forms.ModelForm):
    """Model form to validate data from newsapi.org"""

    class Meta:
        model = NewsSourceModel
        fields = '__all__'


class NewsApiOrgScraper(BaseScraper):
    """Subclass for fetching data from newsapi.org"""

    main_url = 'https://newsapi.org/v2/'

    def create_source(self, data: Dict[str, Any]) -> Optional[NewsSourceModel]:
        domain = get_normalized_domain_name(data['url'])
        form = NewsSourceForm(data={'domain': domain, 'name': data['source'].get('name')}, validate_unique=False)

        if form.is_valid():
            return form.save(commit=False)
        else:
            logger.error(f'Not valid source data {form.errors.as_json()}')
            return None

    def create_news(self, sources_dict: Dict[str, NewsSourceModel], data: Dict[str, Any]) -> Optional[NewsModel]:
        source_domain = get_normalized_domain_name(data['url'])
        source = sources_dict.get(source_domain)

        form = NewsForm(data={
            'author': data['author'], 'title': data['title'], 'description': data['description'],
            'url': data['url'], 'image_url': data['urlToImage'], 'published_at': data['publishedAt'],
            'content': data['content'], 'source': source
        }, validate_unique=False)

        if form.is_valid():
            return form.save(commit=False)
        else:
            logger.error(f'Not valid news data {form.errors.as_json()}')
            return None

