from djangobosssearch.paginator import ResultsetPaginator
from djangobosssearch.providers.boss import (BossWebSearchProvider,
                                             BossSiteSearchProvider,
                                             BossResultSet,
                                             BossSearchException)
from djangobosssearch.providers.base import ResultSet, Result

from django.conf import settings
from django.test import TestCase


class BossInvalidSearchTest(TestCase):

    def setUp(self):
        self.provider = BossWebSearchProvider('invalid', 'invalid')

    def test_invalid_key(self):
        self.assertRaises(BossSearchException,
                          lambda: self.provider.search('test').page(1, 10))


class BossSearchTest(TestCase):

    def setUp(self):
        self.provider = BossWebSearchProvider(settings.BOSS_API_KEY,
                                              settings.BOSS_API_SECRET)

    def test_search_returns_resultset(self):
        self.assertTrue(isinstance(self.provider.search('test'), ResultSet))

    def test_page_method_returns_iterable_results(self):
        results = self.provider.search('test').page(1, 10)
        self.assertTrue(iter(results))
        result = iter(results).next()
        self.assertTrue(isinstance(result, Result))
        self.assertNotEqual('', result.title)
        self.assertNotEqual('', result.description)
        self.assertNotEqual('', result.url)
        self.assertNotEqual('', result.display_url)

    def test_multiple_keywords(self):
        try:
            self.provider.search('test1 test2').page(1, 10)
        except BossSearchException, e:
            self.fail(e)

    def test_get_query(self):
        results = self.provider.search('test')
        self.assertEqual('test', results.get_query())

    def test_paginator(self):
        resultset = self.provider.search('test')
        paginator = ResultsetPaginator(resultset, 50)
        page_obj = paginator.page(1)
        self.assertTrue(len(page_obj.object_list) > 0)
        self.assertTrue(all([isinstance(result, Result)
                             for result in page_obj.object_list]))


class BossSiteSearchTest(BossSearchTest):

    def setUp(self):
        self.provider = BossSiteSearchProvider(
            settings.BOSS_API_KEY, settings.BOSS_API_SECRET, 'lipsum.com')

    def test_count_resultset(self):
        results = self.provider.search('ipsum')
        self.assertTrue(results.count() > 0)


class SpellingTest(TestCase):

    def setUp(self):
        self.provider = BossWebSearchProvider(settings.BOSS_API_KEY,
                                              settings.BOSS_API_SECRET)

    def test_spelling(self):
        resultset = self.provider.search('irland')
        self.assertEqual('ireland', resultset.spelling())


class BossResultsetTest(TestCase):
    def test_get_offset_page_1(self):
        self.assertEqual(0, BossResultSet.get_offset(1, 10))

    def test_get_offset_page_2(self):
        self.assertEqual(11, BossResultSet.get_offset(2, 10))
