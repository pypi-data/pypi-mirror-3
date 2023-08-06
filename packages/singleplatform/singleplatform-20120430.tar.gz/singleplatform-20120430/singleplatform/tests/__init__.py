#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2012 Mike Lewis

import unittest

import singleplatform

try:
    from . import _creds
except ImportError:
    print "Please create a creds.py file in this package, based upon creds.example.py"



class BaseEnpdointTestCase(unittest.TestCase):
    default_locationid = u'haru-7'
    def setUp(self):
        self.api = singleplatform.SinglePlatform(
            _creds.CLIENT_ID,
            _creds.SIGNING_KEY,
            _creds.API_KEY
        )
