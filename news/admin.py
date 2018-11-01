from django.contrib import admin

from news.models import NewsModel, NewsSourceModel

admin.site.register(NewsModel)
admin.site.register(NewsSourceModel)
