# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import logging

log = logging.getLogger(__name__)

_signed_request_algorithm = 'HMAC-SHA256'
_dict_translate = dict(zip(map(ord, u'-_'), u'+/'))


class FacebookSignatureException(Exception):
    """Raised when signed_request is invalid.
    """
    pass


def _base64_url_encode(inp):
    return unicode(base64.b64encode(inp, '-_').strip('=').encode('utf8'))


def _base64_url_decode(inp):
    """ Facebook base64 decoder.

    http://sunilarora.org/parsing-signedrequest-parameter-in-python-bas """
    padding_factor = (4 - len(inp) % 4) % 4
    inp += '=' * padding_factor
    return base64.b64decode(inp.translate(_dict_translate))


def encrypt_signed_request(secret_key, data):
    """Encrypts data the way facebook does for permit testing. Adds algorithm
    key to dict.

    :param data: a dictionary of data to sign.
    """
    data = data.copy()
    data.update(algorithm=_signed_request_algorithm)

    payload = _base64_url_encode(json.dumps(data)).encode('utf8')
    signature = _base64_url_encode(
        hmac.new(
            secret_key.encode('utf8'),
            msg=payload.encode('utf8'),
            digestmod=hashlib.sha256
            ).digest()
        )
    return '%s.%s' % (signature, payload)


def decrypt_signed_request(secret_key, signed_request):
    """ Decrypts signed request sent by facebook. See
    http://developers.facebook.com/docs/authentication/canvas for more
    information.

    returns a dictionary with facebook parameters. """

    if signed_request.count('.') != 1:
        msg = 'signed_request badly formatted.'
        raise FacebookSignatureException(msg)

    signature, payload = signed_request.split('.')

    if not len(signature) > 0 or not len(payload) > 0:
        msg = 'Facebook signature and/or payload with null length.'
        raise FacebookSignatureException(msg)

    try:
        signature = _base64_url_decode(signature)
        data = json.loads(_base64_url_decode(payload))
    except:
        msg = 'Facebook signature or data base64 decoding failed.'
        raise FacebookSignatureException(msg)

    if not hasattr(data, 'get'):
        msg = 'Facebook signed request with invalid data.'
        raise FacebookSignatureException(msg)

    algorithm = data.get('algorithm')
    if not algorithm:
        msg = 'Facebook Signed Request without algorithm information.'
        raise FacebookSignatureException(msg)

    if algorithm.upper() != _signed_request_algorithm:
        msg = 'Facebook signature not encoded with HMAC-SHA256.'
        raise FacebookSignatureException(msg)

    expected_signature = hmac.new(
        secret_key.encode('utf8'),
        msg=payload.encode('utf8'),
        digestmod=hashlib.sha256
        ).digest()

    if signature != expected_signature:
        msg = 'Facebook signed request with invalid signature.'
        raise FacebookSignatureException(msg)

    return data
