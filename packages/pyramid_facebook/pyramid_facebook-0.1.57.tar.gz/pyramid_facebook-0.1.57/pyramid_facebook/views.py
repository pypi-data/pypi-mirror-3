# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json
import logging
import urllib
from string import Template

from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPOk
from pyramid.response import Response
from pyramid.view import (
    view_config,
    view_defaults
    )

from .security import SignedRequestContext, ViewCanvas

log = logging.getLogger(__name__)


js_redirect_tpl = """<html>
  <body>
    <script>
      window.top.location = "%(location)s";
    </script>
  </body>
</html>"""


class Base(object):
    "Base class for views and events"
    def __init__(self, context, request):
        # request and context as properties to prevent modification
        self._context = context
        self._request = request

    @property
    def context(self):
        """Route context which can be of 2 types:

        * :class:`~pyramid_facebook.security.SignedRequestContext`

        * :class:`~pyramid_facebook.security.FacebookCreditsContext`
        """
        return self._context

    @property
    def request(self):
        "Request object for this route."
        return self._request


class OauthAccept(Base):
    "Event sent when a user accepts app authentication."


class OauthDeny(Base):
    "Event sent when a user denies app authentication."


class DisputedOrder(Base):
    "Event sent when a user disputes an order."


class RefundedOrder(Base):
    "Event sent when a user got refunded for an order."


class PlacedItemOrder(Base):
    "Event sent when a user placed an item order."


class EarnedCurrencyOrder(Base):
    "Event sent when a user placed an currency order."


@view_defaults(route_name='facebook_canvas')
class FacebookCanvas(Base):
    """View for `facebook_canvas` route."""

    @view_config(context=HTTPForbidden)
    def prompt_authorize(self):
        """User is not logged in, view prompts user to authorize app:

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
    def canvas(self):
        """When users are logged in, they are authorized to view canvas.

        This view raises :py:exc:`exceptions.NotImplementedError`
        """
        raise NotImplementedError()


@view_defaults(route_name='facebook_canvas_oauth')
class FacebookOAuth(Base):

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
        log.debug('user accepts')
        try:
            self.request.registry.notify(OauthAccept(self.context, self.request))
        except Exception as exc:
            log.error(
                'Oauth accept with context=%r, params=%r: %s',
                self.context,
                self.request.params,
                exc
                )
        return self._redirect_to_canvas()

    @view_config(context=HTTPForbidden, request_param="error")
    def oauth_deny(self):
        log.debug('user denies')
        try:
            self.request.registry.notify(OauthDeny(self.context, self.request))
        except Exception as exc:
            log.error(
                'Oauth deny with context=%r, params=%r: %s',
                self.context,
                self.request.params,
                exc
                )
        return self._redirect_to_canvas()


@view_config(route_name='facebook_payments_status_update_disputed')
def facebook_payments_status_update_disputed(context, request):
    try:
        log.debug('Order Status Update Disputed')
        request.registry.notify(DisputedOrder(context, request))
    except Exception as exc:
        log.error(
            'facebook_payments_status_update_disputed with context=%r, '
            'request.params=%r: %s',
            context,
            request,
            exc
            )
    return HTTPOk()


@view_config(route_name='facebook_payments_status_update_refunded')
def facebook_payments_status_update_refunded(context, request):
    try:
        log.debug('Order Status Update Refunded')
        request.registry.notify(RefundedOrder(context, request))
    except Exception as exc:
        log.error(
            'facebook_payments_status_update_refunded with context=%r, '
            'request.params=%r: %s',
            context,
            request,
            exc
            )
    return HTTPOk()


@view_config(
    route_name='facebook_payments_status_update_placed',
    permission=ViewCanvas,
    renderer='json'
    )
def facebook_payments_status_update_placed(context, request):
    if context.earned_currency_data:
        log.debug('Order Status Update - Earned App Currency')
        event_class = EarnedCurrencyOrder
    else:
        log.debug('Order Status Update - Placed Item Order')
        event_class = PlacedItemOrder
    try:
        request.registry.notify(event_class(context, request))
    except Exception as exc:
        log.error(
            'facebook_payments_status_update_placed with context=%r, '
            'request.params=%r: %s',
            context,
            request,
            exc
            )
        status = 'canceled'
    else:
        log.debug(
            'facebook_payments_status_update_placed settled %r',
            context.order_details
            )
        status = 'settled'
    return {
        'content':{
            'status': status,
            'order_id': context.order_details['order_id'],
            },
        'method':'payments_status_update',
        }
