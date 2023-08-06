# -*- coding: utf-8 -*-
# Copyright (c) 2012 Sebastian Wehrmann
# See also LICENSE.txt

from sw.nikeplus.testing import GOOD_TEST_URL, BAD_TEST_URL
import unittest
import mock



class NikePlusFetcherTest(unittest.TestCase):

    @mock.patch('sw.nikeplus.fetcher.API_URL_V1', GOOD_TEST_URL)
    def test_fetch_returns_status_code_and_content(self):
        from sw.nikeplus.fetcher import NikePlusFetcher
        f = NikePlusFetcher(123)
        status, response = f.fetch()
        self.assertEqual(200, status)
        self.assertIn('plusService', response)

    @mock.patch('sw.nikeplus.fetcher.API_URL_V1', GOOD_TEST_URL)
    def test_fetch_returns_last_response_if_current_request_fails(self):
        from sw.nikeplus.fetcher import NikePlusFetcher
        f = NikePlusFetcher(123)
        status, first_response = f.fetch()
        self.assertEqual(200, status)
        with mock.patch('sw.nikeplus.fetcher.API_URL_V1', BAD_TEST_URL):
            status, response = f.fetch()
        self.assertEqual(404, status)
        self.assertEqual(first_response, response)

    @mock.patch('sw.nikeplus.fetcher.API_URL_V1', BAD_TEST_URL)
    def test_retrieval_can_be_forced_regardless_of_status(self):
        from sw.nikeplus.fetcher import NikePlusFetcher
        f = NikePlusFetcher(123)
        status, response = f.fetch(force=True)
        self.assertEqual(404, status)
        self.assertIn('<title>404 Not Found</title>', response)
