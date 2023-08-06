# -*- coding: utf-8 -*-
from __future__ import absolute_import

import unittest
import webtest

class TestController(unittest.TestCase):

    _app = None

    @property
    def app(self):
        if TestController._app is None:
            from pyramid_facebook import main
            from ...tests import conf
            TestController._app = webtest.TestApp(main(None, **conf))
        return TestController._app

