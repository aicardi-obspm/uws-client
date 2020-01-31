# -*- coding: utf-8 -*-
import unittest
import http.client as httplib
from uws import UWS


class ConnectionTest(unittest.TestCase):
    def test_set_auth_header(self):
        connection = UWS.connection.Connection(
            "http://www.example.com/uws",
            user="admin",
            password="admin"
        )

        try:
            auth_string = connection.auth_string.decode().strip('\n')
        except AttributeError:
            pass

        self.assertEqual(auth_string, "YWRtaW46YWRtaW4=")
        self.assertDictEqual(connection.headers, {'Authorization': 'Basic YWRtaW46YWRtaW4='})

    def test_set_url_http(self):
        connection = UWS.connection.Connection(
            "http://www.example.com/uws/",
            user="admin",
            password="admin"
        )

        self.assertEqual(connection.url, "http://www.example.com/uws")
        self.assertEqual(connection.clean_url, "www.example.com")
        self.assertEqual(connection.base_path, "/uws")
        self.assertIsInstance(connection.connection, httplib.HTTPConnection)

    def test_set_url_https(self):
        connection = UWS.connection.Connection(
            "https://www.example.com/uws/",
            user="admin",
            password="admin"
        )

        self.assertEqual(connection.url, "https://www.example.com/uws")
        self.assertEqual(connection.clean_url, "www.example.com")
        self.assertEqual(connection.base_path, "/uws")
        self.assertIsInstance(connection.connection, httplib.HTTPSConnection)
