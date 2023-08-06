from haystack import indexes
from haystack import site
from ccnews.models import Article

class ArticleIndex(indexes.SearchIndex):
    text = indexes.CharField(
            document=True,
            use_template=True)
    title = indexes.CharField(
            model_attr='title')
    description = indexes.CharField(
            model_attr='description')
    created = indexes.DateTimeField(
            model_attr='created')

    def index_queryset(self):
        return Article.objects.filter(
                status=Article.VISIBLE)

site.register(Article, ArticleIndex)
