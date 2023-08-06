# -*- coding: utf-8 -*-
# Copyright (c) 2012 Sebastian Wehrmann
# See also LICENSE.txt

from sw.nikeplus.testing import GOOD_TEST_URL
import unittest
import mock


class XML2JSONTest(unittest.TestCase):

    def test_parse_empty_string(self):
        from sw.nikeplus.utils import xml2json
        self.assertEqual(None, xml2json(''))

    def test_parse_html(self):
        from sw.nikeplus.utils import xml2json
        html = "<html><head><title>Error</title></head><body>Page not found</body></html>"
        self.assertEqual(
            {'body': 'Page not found',
             'head': {
                 'title': 'Error'}
            }, xml2json(html))

    @mock.patch('sw.nikeplus.fetcher.API_URL_V1', GOOD_TEST_URL)
    def test_parse_nikeplus_data(self):
        from sw.nikeplus.fetcher import NikePlusFetcher
        from sw.nikeplus.utils import xml2json
        f = NikePlusFetcher(1234)
        status, response = f.fetch(force=True)
        self.assertEqual(200, status)
        self.assertEqual(
             {'status': 'success',
              'runListSummary': {
                  'duration': '1683838531',
                  'distance': '5220.999431',
                  'runs': '2',
                  'runDuration': '1683838531',
                  'calories': '390592.48'},
              'runList': [
                  {'distance': '5.6005',
                   'name': None,
                   'gpxId': '7776438c-4e9b-4de5-8d38-600bc636db5d',
                   'terrain': '2',
                   'howFelt': '2',
                   'calories': '452.0',
                   'equipmentType': 'iphone',
                   'syncTime': '2006-10-31T16:38:40+00:00',
                   'intensity': None,
                   'weather': '1',
                   'startTime': '2006-10-31T16:50:07+01:00',
                   'duration': '1752873',
                   'id': '1889752785',
                   'workoutType': 'standard',
                   'description': None},
                  {'distance': '9.6489',
                   'heartrate': {
                       'average': '145',
                       'minimum': '76',
                       'maximum': '157'},
                   'name': None,
                   'hasGpsData': 'false',
                   'gpxId': None,
                   'terrain': None,
                   'howFelt': None,
                   'calories': '693.0',
                   'equipmentType': 'ipod',
                   'syncTime': '2012-03-26T14:56:48+00:00',
                   'intensity': None,
                   'weather': None,
                   'startTime': '2012-03-26T16:01:30+02:00',
                   'duration': '2921638',
                   'id': '556142513',
                   'workoutType': 'heartrate',
                   'description': None}
              ]}, xml2json(response))
