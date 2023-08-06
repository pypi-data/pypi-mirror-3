# -*- coding: utf-8 -*-
# Copyright 2010-2012 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import sys
from piston_mini_client.auth import OAuthAuthorizer, BasicAuthorizer
from unittest import TestCase


class BasicAuthorizerTestCase(TestCase):
    def test_sign_request(self):
        auth = BasicAuthorizer(username='foo', password='bar')
        url = 'http://example.com/api'
        headers = {}
        auth.sign_request(url=url, method='GET', body='', headers=headers)
        self.assertTrue('Authorization' in headers)
        self.assertTrue(headers['Authorization'].startswith('Basic '))
        self.assertEqual(headers['Authorization'], 'Basic Zm9vOmJhcg==')


class OAuthAuthorizerTestCase(TestCase):
    def test_sign_request(self):
        if sys.version_info[0] == 3:
            # Skip on Python 3 as oauth is still broken there.
            # don't use skipIf as it's missing on python2.6
            return
        auth = OAuthAuthorizer('tkey', 'tsecret', 'ckey', 'csecret')
        url = 'http://example.com/api'
        headers = {}
        auth.sign_request(url=url, method='GET', body='', headers=headers)
        self.assertTrue('Authorization' in headers)
        self.assertTrue(headers['Authorization'].startswith('OAuth '))
