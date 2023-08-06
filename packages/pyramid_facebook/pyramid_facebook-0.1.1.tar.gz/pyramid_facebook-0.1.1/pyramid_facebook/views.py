# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
import urllib
from string import Template

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.response import Response
from pyramid.view import (
    view_config,
    view_defaults
    )

from .security import CanvasContext, ViewCanvas

log = logging.getLogger(__name__)


js_redirect_tpl = """<html>
  <body>
    <script>
      window.top.location = "%(location)s";
    </script>
  </body>
</html>"""


class OauthAccept(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request


class OauthDeny(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request


@view_defaults(route_name='facebook_canvas')
class FacebookCanvas(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(context=HTTPForbidden)
    def prompt_authorize(self):
        """Prompt user to authorize app:

        * User is not logged in
        * User is on apps.facebook.com/{namespace}
        """
        log.debug('prompt authorize')
        settings = self.request.registry.settings
        redirect_uri = urllib.quote_plus(
            "%s://apps.facebook.com%s" % (
                self.request.scheme,
                self.request.route_path('facebook_canvas_oauth')
                )
            )
        url = "%s/dialog/oauth/?client_id=%s&redirect_uri=%s&scope=%s" % (
            "https://www.facebook.com",
            settings['facebook.app_id'],
            redirect_uri,
            settings['facebook.scope'].replace(' ', '')
            )
        return Response(js_redirect_tpl % {'location': url})

    @view_config(permission=ViewCanvas)
    def canvas(request):
        """
        * User is logged in
        """
        raise NotImplementedError()


@view_defaults(route_name='facebook_canvas_oauth')
class FacebookOAuth(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _redirect_to_canvas(self):
        p = {
            'location': "%s://apps.facebook.com%s" % (
                self.request.scheme,
                self.request.route_path('facebook_canvas')
                )
            }
        return Response(js_redirect_tpl % p)

    @view_config(permission=ViewCanvas)
    def oauth_accept(self):
        log.debug('user accepts authorization')
        self.request.registry.notify(OauthAccept(self.context, self.request))
        return self._redirect_to_canvas()

    @view_config(context=HTTPForbidden, request_param="error")
    def oauth_deny(self):
        log.debug('user denies authorization')
        self.request.registry.notify(OauthDeny(self.context, self.request))
        return self._redirect_to_canvas()
