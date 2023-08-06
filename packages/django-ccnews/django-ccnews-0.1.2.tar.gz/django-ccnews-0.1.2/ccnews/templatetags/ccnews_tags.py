from datetime import datetime
from django import template
from django.conf import settings
from ccnews.models import Article

register = template.Library()

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
