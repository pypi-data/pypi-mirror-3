from datetime import datetime
from django.test import TestCase
from django.db import models
from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse
from omblog.tests.mock import MockRequest
from omblog import listeners
from omblog import settings as o_settings
from omblog.models import Post
from omblog import views





class DecoratorCacheDisabledTestCases(TestCase):

    def setUp(self):
        # disable the cache
        settings.OMBLOG_CACHE_ENABLED = False
        reload(o_settings)
        # a mock factory
        self.rf = MockRequest()
        # disconnect the signals that clear the cache
        models.signals.pre_save.disconnect(
            listeners.clear_cached_posts,
            sender=Post,
            dispatch_uid='clear_cached_posts')


    def tearDown(self):
        del(settings.OMBLOG_CACHE_ENABLED)
        reload(o_settings)
        # re-attach the listeners
        models.signals.pre_save.connect(
                listeners.clear_cached_posts,
                sender=Post,
                dispatch_uid='clear_cached_posts')

    def test_cache_page_month_cache_enabled_false(self):
        """if no cache is enabled in the settings then
        no caching takes place"""
        # make the date
        d = datetime(
                year=2012,
                month=6,
                day=18,
                minute=2,
                hour=3,
                second=10)
        # request the page
        request = self.rf.get(
                reverse('omblog:month', args=[d.year,d.month]))
        response = views.month(request, d.year, d.month)
        self.assertNotContains(response, 'THISISATESTPOST')
        # now create a blog post
        p = Post()
        p.title = 'THISISATESTPOST'
        p.slug = 'slug'
        p.content = 'This is a test post'
        p.status = p.PUBLISHED
        p.description = 'test post'
        p.created = d
        p.save()
        # now it contains the content
        response = views.month(request, d.year, d.month)
        self.assertContains(response, 'THISISATESTPOST')
        # enabled it again
        settings.OMBLOG_CACHE_ENABLED = True
        reload(o_settings)
        # change the post to hidden and get view again
        p.status = p.HIDDEN
        p.save()
        # not contains
        response = views.month(request, d.year, d.month)
        self.assertNotContains(response, 'THISISATESTPOST')
        # change post status again and save
        p.status = p.PUBLISHED
        p.save()
        # not contains, because the page is cached
        response = views.month(request, d.year, d.month)
        self.assertNotContains(response, 'THISISATESTPOST')

    def test_cache_page_index_cache_enabled_false(self):
        """if no cache is enabled in the settings then
        no caching takes place"""
        # request the page
        request = self.rf.get(reverse('omblog:index'))
        response = views.index(request)
        self.assertNotContains(response, 'THISISATESTPOST')
        # now create a blog post
        p = Post()
        p.title = 'THISISATESTPOST'
        p.slug = 'slug'
        p.content = 'This is a test post'
        p.status = p.PUBLISHED
        p.description = 'test post'
        p.save()
        # now it contains the content
        response = views.index(request)
        self.assertContains(response, 'THISISATESTPOST')
        # enabled it again
        settings.OMBLOG_CACHE_ENABLED = True
        reload(o_settings)
        # change the post to hidden and get view again
        p.status = p.HIDDEN
        p.save()
        # not contains
        response = views.index(request)
        self.assertNotContains(response, 'THISISATESTPOST')
        # change post status again and save
        p.status = p.PUBLISHED
        p.save()
        # not contains, because the page is cached
        response = views.index(request)
        self.assertNotContains(response, 'THISISATESTPOST')
