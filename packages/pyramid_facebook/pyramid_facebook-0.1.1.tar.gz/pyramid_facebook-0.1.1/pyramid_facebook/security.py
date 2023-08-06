# -*- coding: utf-8 -*-
import logging

from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.security import (
    IAuthenticationPolicy,
    Authenticated,
    Everyone,
    Allow
    )
from zope.interface import implements

from .lib import (
    decrypt_signed_request,
    FacebookSignatureException
    )

__all__ = ['FacebookAuthenticationPolicy', 'CanvasContext', 'ViewCanvas']

log = logging.getLogger(__name__)

ViewCanvas = 'view_canvas'


class CanvasContext(object):
    """Security context for facebook canvas routes.
    """
    def __init__(self, request):
        self.__acl__ = [
            (Allow, Authenticated, ViewCanvas),
        ]
        self._fb_data = None

    @property
    def facebook_data(self):
        """Contains facebook data provided in ``signed_request`` parameter.
        """
        return self._fb_data

    @facebook_data.setter
    def facebook_data(self, value):
        if self._fb_data is None:
            self._fb_data = value
        else:
            raise ValueError('Property can be set only once')


class FacebookAuthenticationPolicy(CallbackAuthenticationPolicy):
    implements(IAuthenticationPolicy)

    def __init__(self, secret_key, callback=None):
        log.debug('authentication policy init')
        self.secret_key = secret_key
        self.callback = callback

    def unauthenticated_userid(self, request):
        """
        """
        if request.params.get('signed_request') is None:
            return None

        context = request.context
        if context.facebook_data is None:
            # decrypt signed request once only
            try:
                context.facebook_data = decrypt_signed_request(
                    self.secret_key,
                    request.params["signed_request"]
                    )
            except FacebookSignatureException as e:
                context.facebook_data = dict()
                log.warn('Invalid signature %r', e)
                return None
        try:
            return long(context.facebook_data["user_id"])
        except KeyError as e:
            # user_id not in facebook_data => user has not authorized app
            return None
        except (TypeError, ValueError) as e:
            log.warn('Invalid user id %r', context.facebook_data["user_id"])
        return None
