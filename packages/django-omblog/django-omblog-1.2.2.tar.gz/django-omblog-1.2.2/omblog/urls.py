from django.conf.urls import patterns, url
from omblog.feeds import PostFeed


urlpatterns = patterns('',
    url(r'^feed\.rss$',
        PostFeed(),
        name='feed'),
    url(r'^login/$',
        'django.contrib.auth.views.login',
        {'template_name': 'omblog/login.html'},
        name='login'),
    url(r'^edit/(?P<pk>\d+)/$',
        'omblog.views.edit',
        name='edit'),
    url(r'^tags/(?P<slug>[\w\-]+)/$',
        'omblog.views.tag',
        name='tag'),
    url(r'^(?P<slug>[\w\-]+)/$',
        'omblog.views.post',
        name='post'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        'omblog.views.month',
        name='month'),
    url(r'^$',
        'omblog.views.index',
        name='index'),
)
