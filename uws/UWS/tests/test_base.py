# -*- coding: utf-8 -*-
import unittest

from uws import UWS


class BaseTest(unittest.TestCase):
    def test_validate_and_parse_phase_filter(self):
        filters = {
            'phases': ['COMPLETED', 'PENDING']
        }

        params = UWS.client.Client("/")._validate_and_parse_filters(filters)

        self.assertEqual(params, [('PHASE', 'COMPLETED'), ('PHASE', 'PENDING')])

    def test_validate_and_parse_phase_filter_invalid_phase(self):
        filters = {
            'phases': ['FOO', 'PENDING']
        }

        self.assertRaises(
            UWS.UWSError,
            UWS.client.Client("/")._validate_and_parse_filters,
            filters
        )

    def test_validate_and_parse_after_filter(self):
        filters = {
            'after': '2015-09-10T10:01:02.135'
        }

        params = UWS.client.Client("/")._validate_and_parse_filters(filters)

        self.assertEqual(params, [('AFTER', '2015-09-10T10:01:02.135000')])

    def test_validate_and_parse_after_filter_invalid_date(self):
        filters = {
            'after': '2010-4--'
        }

        self.assertRaises(
            UWS.UWSError,
            UWS.client.Client("/")._validate_and_parse_filters,
            filters
        )

    def test_validate_and_parse_after_filter_time_zone(self):
        filters = {
            'after': '2015-10-03T01:12+2:00'
        }

        params = UWS.client.Client("/")._validate_and_parse_filters(filters)

        self.assertEqual(params, [('AFTER', '2015-10-02T23:12:00')])



    def test_validate_and_parse_last_filter(self):
        filters = {
            'last': '1000'
        }

        params = UWS.client.Client("/")._validate_and_parse_filters(filters)

        self.assertEqual(params, [('LAST', 1000)])

    def test_validate_and_parse_last_filter_float_value(self):
        filters = {
            'last': '100.0'
        }

        self.assertRaises(
            UWS.UWSError,
            UWS.client.Client("/")._validate_and_parse_filters,
            filters
        )

    def test_validate_and_parse_last_filter_negative_value(self):
        filters = {
            'last': '-100'
        }

        self.assertRaises(
            UWS.UWSError,
            UWS.client.Client("/")._validate_and_parse_filters,
            filters
        )

    def test_validate_and_parse_after_last_filter(self):
        filters = {
            'after': '2015-09-10T10:01:02.135',
            'last': '100'
        }

        params = UWS.client.Client("/")._validate_and_parse_filters(filters)

        self.assertEqual(params, [('AFTER', '2015-09-10T10:01:02.135000'),
                                  ('LAST', 100)])

    def test_validate_and_parse_after_last_phase_filter(self):
        filters = {
            'after': '2015-09-10T10:01:02.135',
            'last': '100',
            'phases': ['PENDING', 'ERROR']
        }

        params = UWS.client.Client("/")._validate_and_parse_filters(filters)

        self.assertEqual(params, [('PHASE', 'PENDING'), ('PHASE', 'ERROR'),
                                  ('AFTER', '2015-09-10T10:01:02.135000'), ('LAST', 100)])

    def test_validate_and_parse_wait_negative(self):
        wait = '-1'
        params = UWS.client.Client("/")._validate_and_parse_wait(wait)

        self.assertEqual(params, [('WAIT', -1)])

    def test_validate_and_parse_wait(self):
        wait = '30'
        params = UWS.client.Client("/")._validate_and_parse_wait(wait)

        self.assertEqual(params, [('WAIT', 30)])

    def test_validate_and_parse_wait_invalid_wait(self):
        wait = '30.587'

        self.assertRaises(
            UWS.UWSError,
            UWS.client.Client("/")._validate_and_parse_wait,
            wait
        )

    def test_validate_and_parse_wait_invalid_wait_negative(self):
        wait = '-30'

        self.assertRaises(
            UWS.UWSError,
            UWS.client.Client("/")._validate_and_parse_wait,
            wait
        )

    def test_validate_and_parse_wait_phase(self):
        wait = '30'
        phase = 'EXECUTING'

        params = UWS.client.Client("/")._validate_and_parse_wait(wait, phase)

        self.assertEqual(params, [('WAIT', 30), ('PHASE', 'EXECUTING')])

    def test_validate_and_parse_wait_invalid_phase(self):
        wait = '15'
        phase = 'COMPLETED'

        self.assertRaises(
            UWS.UWSError,
            UWS.client.Client("/")._validate_and_parse_wait,
            wait, phase
        )
