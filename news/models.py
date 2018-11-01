from django.db import models
from django.utils.translation import gettext_lazy as _

from news.utils.url_normalizer import get_normalized_url_path


class NewsSourceModel(models.Model):
    """
    Model for news source

    Attributes
    ----------
    domain : str
        normalized source domain without 'www' part
    name : str

    Methods
    -------
    """
    domain = models.CharField(max_length=253, primary_key=True)
    name = models.CharField(_('Name'), max_length=128)

    class Meta:
        verbose_name = _('Source')

    def __str__(self):
        return f'{self.domain}'


class NewsModel(models.Model):
    """
    Model for news

    Attributes
    ----------
    source
    url
    normalized_path
        Normalized path part of url, will be set automatic in save
    title
    published_at
    author
    description
    image_url
    content

    Methods
    -------
    get_unique_key
        Return unique tuple key for instance
    """

    source = models.ForeignKey(NewsSourceModel, on_delete=models.CASCADE)
    url = models.URLField(_('Url'), max_length=1024)
    normalized_path = models.CharField(_('Normalized path'), max_length=1024, blank=True)
    title = models.TextField(_('Title'), max_length=512)
    published_at = models.DateTimeField(_('Published at'), db_index=True)

    author = models.TextField(_('Author'), blank=True, max_length=128)
    description = models.TextField(_('Description'), blank=True, max_length=512)
    image_url = models.URLField(_('Image url'), blank=True, max_length=1024)
    content = models.TextField(_('Content'), blank=True)

    class Meta:
        # the most stable and important part of article is url,
        # but after analise newsapi.org responses it became clear that
        # url not enough unique (sometimes all articles have home page as url),
        # so we need also to add title to unique key
        # TODO: because we add title in our unique key, will be useful add checks for cases when title changes
        # Domain name can also change, for decrease future problems source is stored in another model,
        # because of that we need only path part of url(without domain name)
        unique_together = ('source', 'normalized_path', 'title')

        verbose_name = _('Source')

    def __str__(self):
        return f'{self.title} id{self.id}'

    def save(self, *args, **kwargs):
        self.normalized_path = get_normalized_url_path(self.url)
        super().save(*args, **kwargs)

    def get_unique_key(self):
        """Return unique tuple key

        Returns
        -------
        tuple : tuple
            Unique key
        """
        return self.source, self.normalized_path, self.title
