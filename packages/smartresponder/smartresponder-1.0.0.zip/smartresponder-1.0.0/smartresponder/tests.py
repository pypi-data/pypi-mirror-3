#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for smartresponder package.
Requires mock >= 0.7.2.
"""

import os
import sys
import urllib
sys.path.insert(0, os.path.abspath('..'))

import unittest
import mock
import smartresponder
import smartresponder.api

API_ID = 'api_id'
API_SECRET = 'api_secret'

class SmartresponderTest(unittest.TestCase):
    def test_api_creation_error(self):
        self.assertRaises(ValueError, lambda: smartresponder.API())

class SignatureTest(unittest.TestCase):
    def test_signature_supports_unicode(self):
        params = {'foo': u'клен'}
        self.assertEqual(
            smartresponder.signature(API_SECRET, params),
            '46abe10921c93d6c45f839cf09c7d19b'
        )

if __name__ == '__main__':
    unittest.main()