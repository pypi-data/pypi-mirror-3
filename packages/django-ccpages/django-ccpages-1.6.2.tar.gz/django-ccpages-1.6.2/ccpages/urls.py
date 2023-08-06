from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^(?P<slug>[\w\-]+)/password\.html$',
        'ccpages.views.password',
        name='password'),
    url(r'^(?P<slug>[\w\-]+)\.html$',
        'ccpages.views.view',
        name='view'),
    url(r'^$',
        'ccpages.views.index',
        name='index'),
)
