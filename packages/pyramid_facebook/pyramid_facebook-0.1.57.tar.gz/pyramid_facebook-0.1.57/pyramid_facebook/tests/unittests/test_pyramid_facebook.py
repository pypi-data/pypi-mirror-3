# -*- coding: utf-8 -*-
import unittest

import mock


class TestFacebookCanvasDecorator(unittest.TestCase):

    def test_init(self):
        from pyramid_facebook import facebook_canvas
        from pyramid_facebook.security import ViewCanvas

        dec = facebook_canvas(**{})

        self.assertEqual(ViewCanvas, dec.permission)
        self.assertEqual('facebook_canvas', dec.route_name)


class TestFacebookPaymentsGetItemsDecorator(unittest.TestCase):

    @mock.patch('pyramid_facebook.venusian')
    def test_call(self, m_venusian):
        from pyramid_facebook import facebook_payments_get_items
        wrapped = mock.Mock()

        dec = facebook_payments_get_items()
        res = dec(wrapped)

        m_venusian.attach.assert_called_once_with(wrapped, dec._register)
        self.assertEqual(wrapped, res)

    def test_register(self):
        from pyramid_facebook.security import ViewCanvas
        from pyramid_facebook import facebook_payments_get_items
        wrapped = mock.Mock()
        scanner = mock.Mock()
        scanner.config = config = mock.Mock()

        dec = facebook_payments_get_items()
        dec._decorate = mock.Mock()

        dec._register(scanner, 'name', wrapped)


        config.add_view.assert_called_once_with(
            view=dec._decorate.return_value,
            permission=ViewCanvas,
            route_name='facebook_payments_get_items',
            renderer='json',
            )

    def test_validate(self):
        from pyramid_facebook import facebook_payments_get_items

        dec = facebook_payments_get_items()

        self.assertRaises(TypeError, dec._validate, ['not_a_dict'])

        self.assertRaises(TypeError, dec._validate, {'not': 'good_keys'})

        bad_type = {
            'title'      : u"A title",
            'description': u"A description",
            'price'      : 1.2,  # not an int
            'image_url'  : "can be a wrong url :-(",
            }
        self.assertRaises(TypeError, dec._validate, bad_type)

        good_content =  {
            'title'      : u"A title",
            'description': u"A description",
            'price'      : 100,
            'image_url'  : u"any str or unicode",
            }

        self.assertEqual(good_content, dec._validate(good_content))

    def test_decorate(self):
        from pyramid_facebook import facebook_payments_get_items
        context = mock.MagicMock()
        request = mock.Mock()
        wrapped = mock.Mock()

        dec = facebook_payments_get_items()
        dec._validate = mock.Mock()

        wrapper = dec._decorate(wrapped)

        # test wrapper call:
        res = wrapper(context, request)

        # assertions:
        dec._validate.assert_called_once_with(wrapped.return_value)
        wrapped.assert_called_once_with(
            context,
            request
            )
        self.assertEqual(res, {
            "content": [dec._validate.return_value],
            "method": "payments_get_items"
            })


class TestPyramidFacebook(unittest.TestCase):

    @mock.patch('pyramid_facebook.request_params_predicate')
    @mock.patch('pyramid_facebook.FacebookAuthenticationPolicy')
    @mock.patch('pyramid_facebook.ACLAuthorizationPolicy')
    def test_includeme(self, m_acl_policy, m_fb_policy, m_predicate):
        settings = {
            'facebook.namespace': 'namespace',
            'facebook.secret_key': 'secret_key'
            }

        config = mock.MagicMock()
        config.registry.settings = settings

        # TEST includeme
        from pyramid_facebook import includeme
        includeme(config)

        # now we check if everything went as expected:
        m_fb_policy.assert_called_once_with('secret_key')
        m_acl_policy.assert_called_once_with()

        config.set_authentication_policy.assert_called_once_with(
            m_fb_policy.return_value
            )
        config.set_authorization_policy.assert_called_once_with(
            m_acl_policy.return_value
            )
        config.scan.assert_called_once_with('pyramid_facebook.views')

        self.assertEqual(5, m_predicate.call_count)

        self.assertEqual(
            mock.call(
                'signed_request',
                'buyer',
                'receiver',
                'order_id',
                'order_info',
                method='payments_get_items'
                ),
            m_predicate.call_args_list[0]
            )

        self.assertEqual(
            mock.call(
                'signed_request',
                'order_details',
                'order_id',
                method='payments_status_update',
                ),
            m_predicate.call_args_list[1]
            )

        self.assertEqual(
            mock.call(status='placed'),
            m_predicate.call_args_list[2]
            )

        self.assertEqual(
            mock.call(status='disputed'),
            m_predicate.call_args_list[3]
            )

        self.assertEqual(
            mock.call(status='refunded'),
            m_predicate.call_args_list[4]
            )

        self.assertEqual(6, config.add_route.call_count)

        call = config.add_route.call_args_list[0]
        expected = mock.call(
            'facebook_canvas',
            '/%s/' % settings['facebook.namespace'],
            request_method='POST',
            request_param='signed_request',
            factory='pyramid_facebook.security.SignedRequestContext'
            )
        self.assertEqual(expected, call)

        call = config.add_route.call_args_list[1]
        expected = mock.call(
            'facebook_canvas_oauth',
            '/%s/oauth' % settings['facebook.namespace'],
            request_method='POST',
            request_param='signed_request',
            factory='pyramid_facebook.security.SignedRequestContext'
            )
        self.assertEqual(expected, call)

        call = config.add_route.call_args_list[2]
        expected = mock.call(
            'facebook_payments_get_items',
            '/%s/credits' % settings['facebook.namespace'],
            request_method='POST',
            custom_predicates=[m_predicate.return_value],
            factory='pyramid_facebook.security.FacebookCreditsContext',
            )
        self.assertEqual(expected, call)

        call = config.add_route.call_args_list[3]
        expected = mock.call(
            'facebook_payments_status_update_placed',
            '/%s/credits' % settings['facebook.namespace'],
            request_method='POST',
            custom_predicates=[m_predicate.return_value,m_predicate.return_value],
            factory='pyramid_facebook.security.FacebookCreditsContext',
            )
        self.assertEqual(expected, call)

        call = config.add_route.call_args_list[4]
        expected = mock.call(
            'facebook_payments_status_update_disputed',
            '/%s/credits' % settings['facebook.namespace'],
            request_method='POST',
            custom_predicates=[m_predicate.return_value,m_predicate.return_value],
            factory='pyramid_facebook.security.FacebookCreditsContext',
            )
        self.assertEqual(expected, call)

        call = config.add_route.call_args_list[5]
        expected = mock.call(
            'facebook_payments_status_update_refunded',
            '/%s/credits' % settings['facebook.namespace'],
            request_method='POST',
            custom_predicates=[m_predicate.return_value,m_predicate.return_value],
            factory='pyramid_facebook.security.FacebookCreditsContext',
            )
        self.assertEqual(expected, call)


    @mock.patch('pyramid_facebook.FacebookAuthenticationPolicy')
    @mock.patch('pyramid_facebook.ACLAuthorizationPolicy')
    def test_includeme_exception(self, m_acl_policy, m_fb_policy):
        from pyramid_facebook import includeme
        bad_settings = {}

        config = mock.MagicMock()
        config.registry.settings = bad_settings

        self.assertRaises(KeyError, includeme, config)

        bad_settings = {
            'facebook.secret_key': 'secret_key'
        }

        config.registry.settings = bad_settings
        self.assertRaises(KeyError, includeme, config)
