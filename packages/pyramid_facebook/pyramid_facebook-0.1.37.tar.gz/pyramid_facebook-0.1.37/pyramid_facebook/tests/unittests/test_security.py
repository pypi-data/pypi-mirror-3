# -*- coding: utf-8 -*-
import unittest

import mock
from pyramid.security import(
    Authenticated,
    Everyone,
    Allow
    )


class TestFacebookCreditsContext(unittest.TestCase):

    @mock.patch('pyramid_facebook.security.json')
    def test_order_details(self, m_json):
        from pyramid_facebook.security import FacebookCreditsContext
        ctx = FacebookCreditsContext(None)
        ctx._fb_data = data = mock.MagicMock()

        self.assertEqual(m_json.loads.return_value, ctx.order_details)
        self.assertEqual(m_json.loads.return_value, ctx._order_details)

        m_json.loads.assert_called_once_with(data['credits']['order_details'])

    @mock.patch('pyramid_facebook.security.json')
    def test_earned_currency_data(self, m_json):
        from pyramid_facebook.security import FacebookCreditsContext
        ctx = FacebookCreditsContext(None)
        ctx._fb_data = data = mock.MagicMock()

        self.assertEqual(
            m_json.loads.return_value['modified'],
            ctx.earned_currency_data
            )
        self.assertEqual(
            m_json.loads.return_value['modified'],
            ctx._earned_currency_data
            )


class TestSignedRequestContext(unittest.TestCase):

    def test_SignedRequestContext_init(self):
        from pyramid_facebook.security import(
            SignedRequestContext,
            ViewCanvas
            )

        ctx = SignedRequestContext(None)
        self.assertListEqual(
            [(Allow, Authenticated, ViewCanvas)],
            ctx.__acl__
            )

    def test_SignedRequestContext_facebook_data(self):
        from pyramid_facebook.security import(
            SignedRequestContext,
            ViewCanvas
            )

        ctx = SignedRequestContext(None)
        self.assertIsNone(ctx._fb_data)
        self.assertIsNone(ctx.facebook_data)
        ctx.facebook_data = "some data"
        self.assertEqual(
            "some data",
            ctx.facebook_data
            )

        self.assertRaises(
            ValueError,
            ctx.__setattr__,
            'facebook_data',
            "some more data"
            )

class TestFacebookAuthenticationPolicy(unittest.TestCase):

    def test_init(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy

        fap = FacebookAuthenticationPolicy('secret key', 'callback')
        self.assertEqual('secret key', fap.secret_key)
        self.assertEqual('callback', fap.callback)

    def test_unauthenticated_userid_no_signed_request(self):
        from pyramid_facebook.lib import encrypt_signed_request
        from pyramid_facebook.security import FacebookAuthenticationPolicy

        # no signed request
        fap = FacebookAuthenticationPolicy('secret key')
        request = mock.MagicMock()
        request.params = dict()

        self.assertIsNone(fap.unauthenticated_userid(request))

    def test_unauthenticated_userid_no_user_id_in_signed_request(self):
        from pyramid_facebook.lib import encrypt_signed_request
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            SignedRequestContext,
            )

        # no user_id in signed request
        fap = FacebookAuthenticationPolicy('secret key')
        signed_request = encrypt_signed_request(
            'secret key',
            {}
            )
        request = mock.MagicMock()
        request.params = dict(signed_request=signed_request)
        request.context = SignedRequestContext(request)

        self.assertIsNone(fap.unauthenticated_userid(request))

    def test_unauthenticated_userid_in_signed_request(self):
        from pyramid_facebook.lib import encrypt_signed_request
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            SignedRequestContext,
            )

        # user id in signed request
        fap = FacebookAuthenticationPolicy('secret key')
        signed_request = encrypt_signed_request(
            'secret key',
            {'user_id': 1234567890}
            )
        request = mock.MagicMock()
        request.params = dict(signed_request=signed_request)
        request.context = SignedRequestContext(request)

        self.assertEqual(
            long(1234567890),
            fap.unauthenticated_userid(request)
            )

    def test_unauthenticated_bad_signature(self):
        from pyramid_facebook.lib import encrypt_signed_request
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            SignedRequestContext,
            )

        # user id in signed request
        fap = FacebookAuthenticationPolicy('secret key')
        signed_request = encrypt_signed_request(
            'another secret key',
            {'user_id': 1234567890}
            )
        request = mock.MagicMock()
        request.params = dict(signed_request=signed_request)
        request.context = SignedRequestContext(request)

        self.assertIsNone(fap.unauthenticated_userid(request))

    def test_unauthenticated_bad_user_id(self):
        from pyramid_facebook.lib import encrypt_signed_request
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            SignedRequestContext,
            )

        # user id in signed request
        fap = FacebookAuthenticationPolicy('secret key')
        signed_request = encrypt_signed_request(
            'secret key',
            {'user_id': "this is not a long"}
            )
        request = mock.MagicMock()
        request.params = dict(signed_request=signed_request)
        request.context = SignedRequestContext(request)

        self.assertIsNone(fap.unauthenticated_userid(request))


    def test_remember(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy

        fap = FacebookAuthenticationPolicy('secret key')

        request = mock.MagicMock()
        principal = "principal"
        kwargs = {"a": "a_val", "b": "b_val"}

        # FacebookAuthenticationPolicy does not support a remember/forget
        # mecanism, user is authenticated on each request
        self.assertListEqual([], fap.remember(request, principal, **kwargs))


    def test_forget(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy

        fap = FacebookAuthenticationPolicy('secret key')

        request = mock.MagicMock()

        # FacebookAuthenticationPolicy does not support a remember/forget
        # mecanism, user is authenticated on each request
        self.assertListEqual([], fap.forget(request))

