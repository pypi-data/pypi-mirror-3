# -*- coding: utf-8 -*-
from __future__ import absolute_import

import unittest
import webtest

from pyramid.config import Configurator


class TestController(unittest.TestCase):

    _app = None

    @property
    def app(self):
        if TestController._app is None:
            from pyramid_facebook import includeme
            from pyramid_facebook.tests import conf
            config = Configurator(settings=conf)
            config.include(includeme)
            TestController._app = webtest.TestApp(config.make_wsgi_app())
        return TestController._app

