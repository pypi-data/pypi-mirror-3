from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>[\w\-]+)$',
        'ccnews.views.view',
        name='view'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        'ccnews.views.month',
        name='month'),
    url(r'^$',
        'ccnews.views.index',
        name='index'),
)
