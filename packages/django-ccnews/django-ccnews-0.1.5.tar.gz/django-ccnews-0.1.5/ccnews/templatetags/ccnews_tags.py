from datetime import datetime
from django import template
from django.conf import settings
from ccnews.models import Article

register = template.Library()

class LatestNewsNode(template.Node):

    def __init__(self, display, varname):
        self.display = display
        self.varname = varname

    def render(self, context):
        news = Article.objects.visible()[:self.display]
        context[self.varname] = news
        return ''

@register.tag
def get_latest_news(parser, token):
    bits = token.contents.split()
    return LatestNewsNode(bits[1], bits[3])

@register.inclusion_tag('ccnews/_js.html')
def ccnews_js():
    return {
        'STATIC_URL': settings.STATIC_URL,
    }

@register.inclusion_tag('ccnews/_css.html')
def ccnews_css():
    return {
        'STATIC_URL': settings.STATIC_URL,
    }

@register.inclusion_tag('ccnews/_nav_breadcrumb.html')
def ccnews_nav_breadcrumb(article_or_date=None):
    """renders out the breadcrumb navigation"""

    try:
        # if it's an article it'll have article attributes
        archive_year = article_or_date.created.year
        archive_month = article_or_date.created.month
        date = article_or_date.created
        article = article_or_date
    except AttributeError:
        # try and set it from the date if not
        try:
            archive_year = article_or_date.year
            archive_month = article_or_date.month
            date = article_or_date
            article = None
        except AttributeError:
            # just set everything to none
            archive_year = None
            archive_month = None
            date = None
            article = None

    return {
        'yr': archive_year,
        'mnth': archive_month,
        'date': date,
        'article': article }

@register.inclusion_tag('ccnews/_nav_local.html')
def ccnews_nav_local(archive_date=None):
    """renders out the local navigation using ccnews/_nav_local.html"""

    # if no archive_date then set it to today
    if not archive_date:
        archive_date = datetime.now()

    return {
        'yr': archive_date.year,
        'mnth': archive_date.month,
        'dates_counts': Article.objects.nav_local()}
