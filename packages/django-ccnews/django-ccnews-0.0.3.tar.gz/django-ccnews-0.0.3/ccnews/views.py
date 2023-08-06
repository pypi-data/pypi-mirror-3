from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from ccnews.models import Article

def index(request):
    """The archive news page"""

    articles = Article.objects.index()

    return render_to_response(
            'ccnews/index.html',
            {'articles': articles},
            RequestContext(request))

def month(request, year, month):
    """The archive news page.
    
    View returns the visible articles for that month along
    with a datetime object for the month"""

    try:
        month = int(month)
        year = int(year)
        archive_date = datetime(year, month, 1, 0, 0, 0)
    except (ValueError, TypeError):
        raise Http404("Bad date info: %s %s" % (year, month))

    articles = Article.objects.for_month(year=year, month=month)

    if articles.count() == 0:
        raise Http404('There are no articles for that month')

    return render_to_response(
            'ccnews/month.html',
            {'articles': articles,
                'archive_date': archive_date},
            RequestContext(request))

def view(request, year, month, slug):
    """The view news page"""

    try:
        article = Article.objects.visible().get(slug=slug)
    except Article.DoesNotExist:
        raise Http404

    return render_to_response(
            'ccnews/view.html',
            {'article': article},
            RequestContext(request))
