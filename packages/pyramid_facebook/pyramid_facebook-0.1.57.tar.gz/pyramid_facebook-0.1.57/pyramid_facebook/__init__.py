# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging

import json
import venusian
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy

from .lib import request_params_predicate
from .security import FacebookAuthenticationPolicy, ViewCanvas

__all__ = [
    'includeme',
    'facebook_canvas'
    'facebook_payments_get_items',
    ]

log = logging.getLogger(__name__)


def includeme(config):
    """Executed when including ``pyramid_facebook``.

    ``pyramid_facebook`` setup:

    * ACL Authorization with :class:`~pyramid.authorization.ACLAuthorizationPolicy`
      using :meth:`config.set_authorization_policy <pyramid.config.Configurator.set_authorization_policy>`
    * Authentication with :class:`~pyramid_facebook.security.FacebookAuthenticationPolicy`
      using :meth:`config.set_authentication_policy <pyramid.config.Configurator.set_authentication_policy>`

    It adds routes which all requires :

    * a ``POST`` method, ``GET`` method will be considered as not found and
      will return a HTTP 404)
    * a ``signed_request`` parameter in body as defined on `Facebook
      documentation
      <http://developers.facebook.com/docs/authentication/signed_request/>`_.

    Routes added:

    * ``facebook_canvas`` associated to url ``/{namespace}/`` that musts be
      configured as canvas callback url in facebook application settings.

    * ``facebook_canvas_oauth`` associated to url ``/{namespace}/oauth`` for
      authentication.

    * ``facebook_payments_get_items`` associated to url ``/{namespace}/credits``.

    * ``facebook_payments_status_update_placed`` associated to url
      ``/{namespace}/credits``.

    * ``facebook_payments_status_update_disputed`` associated to url
      ``/{namespace}/credits``.

    * ``facebook_payments_status_update_refunded`` associated to url
      ``/{namespace}/credits``.
    """
    log.debug('config: %r', config)
    settings = config.registry.settings

    config.set_authentication_policy(
        FacebookAuthenticationPolicy(settings['facebook.secret_key'])
        )
    config.set_authorization_policy(ACLAuthorizationPolicy())

    facebook_path = '/%s' % settings['facebook.namespace']

    # Facebook canvas ##########################################################
    log.debug('Adding route facebook_canvas: %s/', facebook_path)
    config.add_route(
        'facebook_canvas',
        '%s/' % facebook_path,
        request_method='POST',
        request_param='signed_request',
        factory='pyramid_facebook.security.SignedRequestContext',
        )

    log.debug('Adding route facebook_canvas_oauth: %s/oauth', facebook_path)
    config.add_route(
        'facebook_canvas_oauth',
        '%s/oauth' % facebook_path,
        request_method='POST',
        request_param='signed_request',
        factory='pyramid_facebook.security.SignedRequestContext',
        )

    # Facebook credits #########################################################

    log.debug(
        'Adding route "facebook_payments_get_items": %s/credits',
        facebook_path
        )
    config.add_route(
        'facebook_payments_get_items',
        '%s/credits' % facebook_path,
        request_method='POST',
        custom_predicates=[
            request_params_predicate(
                'signed_request',
                'buyer',
                'receiver',
                'order_id',
                'order_info',
                method='payments_get_items',
                )
            ],
        factory='pyramid_facebook.security.FacebookCreditsContext',
        )

    update_predicate = request_params_predicate(
        'signed_request',
        'order_details',
        'order_id',
        method='payments_status_update',
        )

    log.debug(
        'Adding route "facebook_payments_status_update_placed": %s/credits',
        facebook_path
        )
    config.add_route(
        'facebook_payments_status_update_placed',
        '%s/credits' % facebook_path,
        request_method='POST',
        custom_predicates=[
            update_predicate,
            request_params_predicate(status='placed'),
            ],
        factory='pyramid_facebook.security.FacebookCreditsContext',
        )

    log.debug(
        'Adding route "facebook_payments_status_update_disputed": %s/credits',
        facebook_path
        )
    config.add_route(
        'facebook_payments_status_update_disputed',
        '%s/credits' % facebook_path,
        request_method='POST',
        custom_predicates=[
            update_predicate,
            request_params_predicate(status='disputed'),
            ],
        factory='pyramid_facebook.security.FacebookCreditsContext',
        )

    log.debug(
        'Adding route "facebook_payments_status_update_refunded": %s/credits',
        facebook_path
        )
    config.add_route(
        'facebook_payments_status_update_refunded',
        '%s/credits' % facebook_path,
        request_method='POST',
        custom_predicates=[
            update_predicate,
            request_params_predicate(status='refunded'),
            ],
        factory='pyramid_facebook.security.FacebookCreditsContext',
        )

    config.scan('pyramid_facebook.views')


class facebook_canvas(view_config):
    """Decorator that registers a view for the ``facebook_canvas`` route
    with the ``view_canvas`` permission.

    Accepts same arguments as :class:`~pyramid.view.view_config`::

        @facebook_canvas(renderer='canvas.mako')
        def canvas(context, request):
            return {
                'title': 'A great Facebook Game'
                }
    """
    def __init__(self, **kwargs):
        config = kwargs.copy()
        config.update({
            'permission': ViewCanvas,
            'route_name': 'facebook_canvas'
            })
        super(facebook_canvas, self).__init__(**config)


class facebook_payments_get_items(object):
    """Decorator to register the function to process facebook credits
    `payments_get_items <http://developers.facebook.com/docs/credits/callback/#payments_get_items>`_
    .

    Decorated function receives 2 positional parameters and 1 keyword argument:

    * ``context``: The :class:`~pyramid_facebook.security.SignedRequestContext`
      the request is associated with. ``context.facebook_data["user"]`` gives
      information about user's locale which would permit to return different
      languages.

    * ``request``: The request itself.

    It is possible to access `order_info` via :attr:`context.order_info
    <pyramid_facebook.security.FacebookCreditsContext.order_info>`:

    Decorated function must return a dictionary structured as::

        {
            # Required:
            "title":       "100 diamonds",
            "description": "100 shiny diamonds!",
            "price":       1000,
            "image_url":   "http://hadriendavid.com/images/100dimonds.png",

            # Optionnal (according to facebook doc):
            "item_id": "123",
            "data":    "whatever"
        }

    Example::

        @facebook_payments_get_items()
        def get_item(context, request):
            ...
            return {
                "title": a_title,
                "description": a_description,
                "price": a_price_in_facebook_credits,
                "image_url": an_image_url
                }
    """
    def __call__(self, wrapped):
        # as documented on http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/hooks.html#registering-configuration-decorators
        venusian.attach(wrapped, self._register)
        return wrapped

    def _register(self, scanner, name, wrapped):
        """Register view to pyramid framework.
        """
        config = scanner.config
        config.add_view(
            view=self._decorate(wrapped),
            permission=ViewCanvas,
            route_name='facebook_payments_get_items',
            renderer='json',
            )

    def _validate(self, item_content):
        "Validate item content"
        if not isinstance(item_content, dict):
            raise TypeError('dict expected, received %s' % type(item_content))
        expected = {
            'title'      : (str, unicode,),
            'description': (str, unicode,),
            'price'      : (int,         ),
            'image_url'  : (str, unicode,),
            }
        for k, v in expected.iteritems():
            if type(item_content.get(k)) not in v:
                raise TypeError('Expected %r, received %r' % (
                    expected,
                    item_content
                    ))
        return item_content

    def _decorate(self, wrapped):
        def wrapper(context, request):
            info = context.facebook_data["credits"]["order_info"]
            result = self._validate(wrapped(context, request))
            return {
                "content": [result],
                "method": "payments_get_items"
                }
        return wrapper
