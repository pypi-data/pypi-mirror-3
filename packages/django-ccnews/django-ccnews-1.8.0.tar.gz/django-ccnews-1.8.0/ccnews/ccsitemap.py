import ccsitemaps
from ccnews.models import Article


class ArticleSiteMap(ccsitemaps.SiteMap):

    model = Article

    @staticmethod
    def last_mod():
        try:
            last_mod = Article.objects\
                .visible()\
                .order_by('-modified')[0]
            return last_mod.modified
        except IndexError:
            return None

    @staticmethod
    def get_objects():
        return Article.objects.visible()

ccsitemaps.register(ArticleSiteMap)
