from django.views.generic import ListView

from news.models import NewsModel


class NewsListView(ListView):
    """News list html representation"""

    model = NewsModel
    paginate_by = 20
    template_name = 'news_list.html'
    ordering = '-published_at'
