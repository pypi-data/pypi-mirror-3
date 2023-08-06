# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator

from .security import FacebookAuthenticationPolicy

__all__ = ['includeme', 'main']

log = logging.getLogger(__name__)


def main(global_config, **settings):
    log.debug('global_config: %r\nsettings: %r', global_config, settings)
    config = Configurator(settings=settings)
    config.include(includeme)
    return config.make_wsgi_app()


def includeme(config):
    log.debug('config: %r', config)
    settings = config.registry.settings

    config.set_authentication_policy(
        FacebookAuthenticationPolicy(settings['facebook.secret_key'])
        )
    config.set_authorization_policy(ACLAuthorizationPolicy())

    facebook_path = '/%s' % settings['facebook.namespace']

    config.scan()

    config.add_route(
        'facebook_canvas',
        '%s/' % facebook_path,
        request_method='POST',
        request_param='signed_request',
        factory='pyramid_facebook.security.CanvasContext',
        )

    config.add_route(
        'facebook_canvas_oauth',
        '%s/oauth' % facebook_path,
        request_method='POST',
        request_param='signed_request',
        factory='pyramid_facebook.security.CanvasContext',
        )

    config.commit()
