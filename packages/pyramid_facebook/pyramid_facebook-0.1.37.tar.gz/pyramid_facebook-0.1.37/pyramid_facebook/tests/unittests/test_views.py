import unittest

import mock
from pyramid import testing
from pyramid.request import Request
from pyramid.response import Response
from pyramid.httpexceptions import HTTPOk


def _get_settings():
    return {
        'facebook.scope': 'mail, birthday',
        'facebook.app_id': '1234567890'
    }


class TestFacebookPaymentsCallback(unittest.TestCase):

    @mock.patch('pyramid_facebook.views.DisputedOrder')
    def test_facebook_payments_status_update_disputed(self, m_order):
        from pyramid_facebook.views import facebook_payments_status_update_disputed
        ctx = mock.Mock()
        req = mock.Mock()

        res = facebook_payments_status_update_disputed(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)
        self.assertIsInstance(res, HTTPOk)

        # test exception
        req.reset_mock()
        req.registry.notify.side_effect = Exception('boom!')

        res = facebook_payments_status_update_disputed(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)
        self.assertIsInstance(res, HTTPOk)

    @mock.patch('pyramid_facebook.views.RefundedOrder')
    def test_facebook_payments_status_update_refunded(self, m_order):
        from pyramid_facebook.views import facebook_payments_status_update_refunded
        ctx = mock.Mock()
        req = mock.Mock()

        res = facebook_payments_status_update_refunded(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)
        self.assertIsInstance(res, HTTPOk)

        # test exception
        req.reset_mock()
        req.registry.notify.side_effect = Exception('boom!')

        res = facebook_payments_status_update_refunded(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)
        self.assertIsInstance(res, HTTPOk)


    @mock.patch('pyramid_facebook.views.EarnedCurrencyOrder')
    def test_facebook_payments_status_update_placed_currency_app_order(self, m_order):
        from pyramid_facebook.views import facebook_payments_status_update_placed
        ctx = mock.MagicMock()
        req = mock.Mock()

        res = facebook_payments_status_update_placed(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)

        expected = {
            'content':{
                'status': 'settled',
                'order_id': ctx.order_details['order_id']
                },
            'method': 'payments_status_update',
            }
        self.assertDictEqual(expected, res)

    @mock.patch('pyramid_facebook.views.PlacedItemOrder')
    def test_facebook_payments_status_update_placed_item_order(self, m_order):
        from pyramid_facebook.views import facebook_payments_status_update_placed
        ctx = mock.MagicMock()
        ctx.earned_currency_data = None
        req = mock.Mock()

        res = facebook_payments_status_update_placed(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)

    @mock.patch('pyramid_facebook.views.EarnedCurrencyOrder')
    def test_facebook_payments_status_update_exception(self, m_order):
        from pyramid_facebook.views import facebook_payments_status_update_placed
        ctx = mock.MagicMock()
        req = mock.Mock()
        req.registry.notify.side_effect = Exception('boooom!')

        res = facebook_payments_status_update_placed(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)

        expected = {
            'content':{
                'status': 'canceled',
                'order_id': ctx.order_details['order_id']
                },
            'method': 'payments_status_update',
            }
        self.assertDictEqual(expected, res)


class TestFacebookCanvas(unittest.TestCase):

    def test_init(self):
        from pyramid_facebook.views import FacebookCanvas
        request = mock.MagicMock()
        canvas = FacebookCanvas(request.context, request)
        self.assertEqual(request, canvas.request)
        self.assertEqual(request.context, canvas.context)

    def test_prompt_authorize(self):
        from pyramid_facebook.views import FacebookCanvas

        settings = _get_settings()

        request = mock.MagicMock()
        request.scheme = 'http'
        request.route_path.return_value = '/facebook/oauth'
        request.registry.settings = settings

        canvas = FacebookCanvas(request.context, request)

        result = canvas.prompt_authorize()

        request.route_path.assert_called_once_with('facebook_canvas_oauth')

        expected = """200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 234

<html>
  <body>
    <script>
      window.top.location = "https://www.facebook.com/dialog/oauth/?client_id=1234567890&redirect_uri=http%3A%2F%2Fapps.facebook.com%2Ffacebook%2Foauth&scope=mail,birthday";
    </script>
  </body>
</html>"""
        self.assertEqual(expected, str(result))

    def test_canvas(self):
        from pyramid_facebook.views import FacebookCanvas
        request = mock.MagicMock()
        canvas = FacebookCanvas(request.context, request)
        self.assertRaises(Exception, canvas.canvas)


class TestFacebookOauth(unittest.TestCase):

    def test_init(self):
        from pyramid_facebook.views import FacebookOAuth
        request = mock.MagicMock()
        canvas = FacebookOAuth(request.context, request)
        self.assertEqual(request, canvas.request)
        self.assertEqual(request.context, canvas.context)

    def test_oauth_accept(self):
        from pyramid_facebook.views import (
            FacebookOAuth,
            OauthAccept
            )
        settings = _get_settings()

        request = mock.MagicMock()
        request.scheme = 'http'
        request.route_path.return_value = '/facebook/'
        request.registry.settings = settings

        view = FacebookOAuth(request.context, request)

        result = view.oauth_accept()

        request.route_path.assert_called_once_with('facebook_canvas')
        self.assertTrue(request.registry.notify.called)

        self.assertIsInstance(
            request.registry.notify.call_args[0][0],
            OauthAccept
            )

        expected = """200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 126

<html>
  <body>
    <script>
      window.top.location = "http://apps.facebook.com/facebook/";
    </script>
  </body>
</html>"""
        self.assertEqual(expected, str(result))

    def test_oauth_deny(self):
        from pyramid_facebook.views import (
            FacebookOAuth,
            OauthDeny
            )
        settings = _get_settings()

        request = mock.MagicMock()
        request.scheme = 'http'
        request.route_path.return_value = '/facebook/'
        request.registry.settings = settings

        view = FacebookOAuth(request.context, request)

        result = view.oauth_deny()

        request.route_path.assert_called_once_with('facebook_canvas')
        self.assertTrue(request.registry.notify.called)

        self.assertIsInstance(
            request.registry.notify.call_args[0][0],
            OauthDeny
            )

        expected = """200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 126

<html>
  <body>
    <script>
      window.top.location = "http://apps.facebook.com/facebook/";
    </script>
  </body>
</html>"""
        self.assertEqual(expected, str(result))


