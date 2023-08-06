# -*- coding: utf-8 -*-
from datetime import datetime
from django.test import TestCase
from django.conf import settings
from omblog import settings as omblog_settings

class SettingTestCases(TestCase):
    """Ensure that settings can be correctly overriden"""

    def test_override_cache_enabled(self):
        settings.OMBLOG_CACHE_ENABLED = False
        reload(omblog_settings)
        self.assertEqual(omblog_settings.CACHE_ENABLED, False)
        # revert it
        del(settings.OMBLOG_CACHE_ENABLED)

    def test_cache_enabled(self):
        reload(omblog_settings)
        self.assertEqual(omblog_settings.CACHE_ENABLED, True)

    def test_override_cache_prefix(self):
        settings.OMBLOG_CACHE_PREFIX = 'testerburger_'
        reload(omblog_settings)
        self.assertEqual(omblog_settings.CACHE_PREFIX, 'testerburger_')
        # revert it
        del(settings.OMBLOG_CACHE_PREFIX)

    def test_cache_prefix(self):
        reload(omblog_settings)
        self.assertEqual(omblog_settings.CACHE_PREFIX, 'omblog_')

    def test_override_show_ideas_if_logged_in(self):
        settings.OMBLOG_SHOW_IDEAS_IF_LOGGED_IN = False
        reload(omblog_settings)
        self.assertEqual(omblog_settings.SHOW_IDEAS_IF_LOGGED_IN, False)
        # revert it
        del(settings.OMBLOG_SHOW_IDEAS_IF_LOGGED_IN)

    def test_show_ideas_if_logged_in(self):
        reload(omblog_settings)
        self.assertEqual(omblog_settings.SHOW_IDEAS_IF_LOGGED_IN, True)

    def test_override_show_hidden_if_logged_in(self):
        settings.OMBLOG_SHOW_HIDDEN_IF_LOGGED_IN = False
        reload(omblog_settings)
        self.assertEqual(omblog_settings.SHOW_HIDDEN_IF_LOGGED_IN, False)
        # revert it
        del(settings.OMBLOG_SHOW_HIDDEN_IF_LOGGED_IN)

    def test_show_hidden_if_logged_in(self):
        reload(omblog_settings)
        self.assertEqual(omblog_settings.SHOW_HIDDEN_IF_LOGGED_IN, True)

    def test_override_show_drafts_if_logged_in(self):
        settings.OMBLOG_SHOW_DRAFTS_IF_LOGGED_IN = False
        reload(omblog_settings)
        self.assertEqual(omblog_settings.SHOW_DRAFTS_IF_LOGGED_IN, False)
        # revert it
        del(settings.OMBLOG_SHOW_DRAFTS_IF_LOGGED_IN)

    def test_show_drafts_if_logged_in(self):
        reload(omblog_settings)
        self.assertEqual(omblog_settings.SHOW_DRAFTS_IF_LOGGED_IN, True)

    def test_override_index_items(self):
        settings.OMBLOG_INDEX_ITEMS = 5
        reload(omblog_settings)
        self.assertEqual(omblog_settings.INDEX_ITEMS, 5)
        # revert it
        del(settings.OMBLOG_INDEX_ITEMS)

    def test_default_index_items(self):
        reload(omblog_settings)
        self.assertEqual(omblog_settings.INDEX_ITEMS, 20)
