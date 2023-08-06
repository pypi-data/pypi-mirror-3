# -*- coding: utf-8 -*-
import json
import logging

from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.security import (
    IAuthenticationPolicy,
    Authenticated,
    Everyone,
    Allow
    )

from zope.interface import implementer

from .lib import (
    decrypt_signed_request,
    FacebookSignatureException
    )

__all__ = ['FacebookAuthenticationPolicy', 'SignedRequestContext', 'ViewCanvas',
    'FacebookCreditsContext']

log = logging.getLogger(__name__)

ViewCanvas = 'view_canvas'


class SignedRequestContext(object):
    "Security context for facebook signed request routes."

    def __init__(self, request):
        self.__acl__ = [
            (Allow, Authenticated, ViewCanvas),
        ]
        self._fb_data = None

    @property
    def facebook_data(self):
        """Contains facebook data provided in ``signed_request`` parameter
        decrypted with :func:`decrypt_signed_request <pyramid_facebook.lib.decrypt_signed_request>`.
        """
        return self._fb_data

    @facebook_data.setter
    def facebook_data(self, value):
        if self._fb_data is None:
            self._fb_data = value
        else:
            raise ValueError('Property can be set only once')

    def __repr__(self):
        return '<%s facebook_data=%r>' % (
            self.__class__.__name__,
            self._fb_data
            )


class FacebookCreditsContext(SignedRequestContext):
    "Context for facebook credits callback requests."

    @property
    def order_details(self):
        """Order details received in `facebook credits callback for payment
        status updates <http://developers.facebook.com/docs/credits/callback/#payments_status_update>`_."""
        if not hasattr(self, '_order_details'):
            self._order_details = json.loads(
                self.facebook_data['credits']['order_details']
                )
        return self._order_details

    @property
    def order_info(self):
        """Order info being the order information passed when the `FB.ui method
        <http://developers.facebook.com/docs/reference/javascript/FB.ui/>`_
        is invoked."""
        return self.facebook_data["credits"]["order_info"]

    @property
    def earned_currency_data(self):
        """Modified field received in `facebook credits callback for payment
        status update for earned app currency
        <http://developers.facebook.com/docs/credits/callback/#payments_status_update_earn_app_currency>`_."""
        if not hasattr(self, '_earned_currency_data'):
            data = self.order_details['items'][0]['data']
            if data:
                data = json.loads(data)['modified']
            self._earned_currency_data = data
        return self._earned_currency_data


@implementer(IAuthenticationPolicy)
class FacebookAuthenticationPolicy(CallbackAuthenticationPolicy):
    """A policy which authenticates user from ``signed_request`` parameter:

    * It decrypts ``signed_request`` as explained on `Facebook documentation
      <http://developers.facebook.com/docs/authentication/signed_request/>`_
      using :func:`decrypt_signed_request <pyramid_facebook.lib.decrypt_signed_request>`

    * It assigns :py:attr:`context.facebook_data <pyramid_facebook.security.SignedRequestContext.facebook_data>`
      with decrypted data.

    See `CallbackAuthenticationPolicy code <https://github.com/Pylons/pyramid/blob/master/pyramid/authentication.py#L35>`_
    for more info.
    """

    def __init__(self, secret_key, callback=None):
        log.debug('authentication policy init')
        self.secret_key = secret_key
        self.callback = callback

    def unauthenticated_userid(self, request):
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
        except KeyError:
            # user_id not in facebook_data => user has not authorized app
            return None
        except (TypeError, ValueError):
            log.warn('Invalid user id %r', context.facebook_data["user_id"])
        return None


    def remember(self, request, principal, **kwargs):
        return []


    def forget(self, request):
        return []
