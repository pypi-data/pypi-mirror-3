# -*- coding: utf-8 -*-
import unittest

import mock


class TestLib(unittest.TestCase):

    def test_base64_encode_decode(self):
        from pyramid_facebook.lib import _base64_url_decode, _base64_url_encode

        msg = u'eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTI5NzExMDA0OCwidXNlciI6eyJsb2NhbGUiOiJlbl9VUyIsImNvdW50cnkiOiJjYSJ9fQ'
        data = u'{"algorithm":"HMAC-SHA256","issued_at":1297110048,"user":{"locale":"en_US","country":"ca"}}'

        self.assertEqual(data, _base64_url_decode(msg))
        self.assertEqual(msg, _base64_url_encode(data))
        self.assertEqual(
            msg,
            _base64_url_encode(
                _base64_url_decode(
                    _base64_url_encode(data)
                    )
                )
            )

    def test_encrypt_decrypt_request(self):
        from pyramid_facebook.lib import (
            encrypt_signed_request,
            decrypt_signed_request,
            )
        data = {
            u'issued_at': 1297110048,
            u'user': {
                u'locale': u'en_US',
                u'country': u'ca'
                },
            u'algorithm': u'HMAC-SHA256'
            }

        req = encrypt_signed_request('secret key', data)
        res = decrypt_signed_request('secret key', req)
        self.assertEqual(set(data.keys()), set(res.keys()))
        self.assertEqual(str(data), str(res))

    def test_decrypt_valid_signed_request_exception(self):
        from pyramid_facebook.lib import (
            FacebookSignatureException,
            decrypt_signed_request,
            encrypt_signed_request,
            )

        self.assertRaises(
            FacebookSignatureException,
            decrypt_signed_request,
            'secret_key',
            'without any dot'
            )

        self.assertRaises(
            FacebookSignatureException,
            decrypt_signed_request,
            'secret_key',
            'signature.'
            )

        self.assertRaises(
            FacebookSignatureException,
            decrypt_signed_request,
            'secret_key',
            '.payload'
            )

        self.assertRaises(
            FacebookSignatureException,
            decrypt_signed_request,
            'secret_key',
            'signature.payload'
            )

    @mock.patch('pyramid_facebook.lib.json')
    def test_decrypt_signed_request_exeption_json(self, m_json):
        from pyramid_facebook.lib import (
            _base64_url_encode,
            decrypt_signed_request,
            encrypt_signed_request,
            FacebookSignatureException
            )

        m_json.loads.return_value = []

        self.assertRaises(
            FacebookSignatureException,
            decrypt_signed_request,
            'secret key',
            "%s.payload" % _base64_url_encode("some input"),
            )


        m_json.loads.return_value = {}

        self.assertRaises(
            FacebookSignatureException,
            decrypt_signed_request,
            'secret key',
            "%s.payload" % _base64_url_encode("some input"),
            )


        m_json.loads.return_value = {'algorithm': 'NOT HMAC-SHA256'}

        self.assertRaises(
            FacebookSignatureException,
            decrypt_signed_request,
            'secret key',
            "%s.payload" % _base64_url_encode("some input"),
            )

    def test_decrypt_request_exception_wrong_signature(self):
        from pyramid_facebook.lib import (
            decrypt_signed_request,
            encrypt_signed_request,
            FacebookSignatureException
            )

        signed_request = encrypt_signed_request(
            'a secret key',
            {}
            )

        self.assertRaises(
            FacebookSignatureException,
            decrypt_signed_request,
            'another key',
            signed_request
            )

    def test_request_params_predicate(self):
        from pyramid_facebook.lib import request_params_predicate

        predicate = request_params_predicate('a', 'b', 'c', d=123, e='yo')

        request = mock.Mock()
        request.params = dict(a=1, b=2, c=3, d=123, e='yo')
        self.assert_(predicate(None, request))

        request.params = dict(a=1, b=2)
        self.assertFalse(predicate(None, request))

        request.params = dict(a=1, b=2, c=1, d=321, e='oy')
        self.assertFalse(predicate(None, request))
