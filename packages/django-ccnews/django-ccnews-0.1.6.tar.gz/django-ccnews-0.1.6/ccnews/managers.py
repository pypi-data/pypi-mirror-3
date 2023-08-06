import operator
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from django.db import models
from ccnews import settings as c_settings


class ArticleManager(models.Manager):

    def index(self):
        """returns the news items for the index.

        The amount returned is dependant on c_settings.CCNEWS_INDEX_ITEMS
        """
        slice_value = c_settings.CCNEWS_INDEX_ITEMS
        return self.visible()[:slice_value]


    def visible(self):
        """returns the visible news"""
        return super(ArticleManager, self)\
                .get_query_set()\
                .filter(status=self.model.VISIBLE)

    def nav_local(self):
        """returns the years and months for which there are posts.

        Returns an ordered dict with the following structure:-

        {'2012_05': [datetime(2012,5,20,0,0,0), count}

        """
        articles = self.visible()
        dates = OrderedDict()
        for article in articles:
            key = article.created.strftime('%Y_%m')
            try:
                dates[key][1] = dates[key][1] + 1
            except KeyError:
                dates[key] = [article.created, 1]
        return dates

    def for_month(self, month, year):
        """returns the articles for a given month in a year"""
        return super(ArticleManager, self)\
                .get_query_set()\
                .filter(
                        status=self.model.VISIBLE,
                        created__year=year,
                        created__month=month)
