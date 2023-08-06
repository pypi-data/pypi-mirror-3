# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json

from ...tests import get_signed_request, conf
from ..functionals import TestController

# Do not ask why facebook payment callback is that twisted:
# 1 - Read the docs https://developers.facebook.com/docs/credits/callback/
# 2 - if headache take aspirin and go back to point 1

USER_ID = 123
ORDER_ID = 987

credits_data = {
        'buyer': USER_ID,
        'receiver': USER_ID,
        'order_id': ORDER_ID,
        'order_info': '{"item_id":"1"}'
        }

request_data = {
    'user':{
        'country': 'us',
        'locale': 'en_US',
        'age': {
            'min': 21,
            'max': 45
            }
        },
    'user_id': USER_ID,
    'oauth_token':'AAAE0yTNwOxgBABXrDk9tNR0DoWyxwuLLNtpaJCRve8jbUZCr4YbxiIJqdwtHHZBt5uK8wV9ELHFfZBl9DmZAyvcXOuTZC9JZC22BCSfzky1gZDZD',
    'expires': 1325210400,
    'issued_at': 1325203762
    }

order_details = {
    'order_id': ORDER_ID,
    'buyer': USER_ID,
    'app': 9876,
    'receiver': USER_ID,
    'amount': 10,
    'time_placed': 1329243276,
    'update_time': 1329243277,
    'data':'',
    'items':[{
        'item_id': '0',
        'title':'100 Diamonds',
        'description': 'Spend Diamonds in dimonds game.',
        'image_url': 'http://image.com/diamonds.png',
        'product_url':'',
        'price': 10,
        'data':''
        }],
    'status': 'placed'}

earned_app_currency = {
    'modified':{
        'product': 'URL_TO_APP_CURR_WEBPAGE',
        'product_title': 'Diamonds',
        'product_amount': 3,
        'credits_amount':10
        }
    }


class TestFacebookCredits(TestController):
    """Test based on fb documentation:
    https://developers.facebook.com/docs/credits/callback/"""

    def test_payments_get_items(self):
        params = request_data.copy()
        params.update(credits=credits_data)
        params = {
            'signed_request': get_signed_request(**params),
            'method': 'payments_get_items'
            }
        params.update(credits_data)

        self.app.post(
            '/%s/credits' % conf['facebook.namespace'],
            params,
            status=404
            )

    def test_payments_status_update_placed_item_order(self):
        params = request_data.copy()
        params.update(
            {
            'credits':{
                'order_details': json.dumps(order_details.copy()),
                'status': 'placed',
                'order_id': ORDER_ID
                }
            })

        params = {
            'signed_request': get_signed_request(**params),
            'order_details': json.dumps(order_details.copy()),
            'order_id': ORDER_ID,
            'method': 'payments_status_update',
            'status': 'placed',
            }

        result = self.app.post(
            '/%s/credits' % conf['facebook.namespace'],
            params,
            )

        expected = {
            'content': {
                'status': 'settled',
                'order_id': 987
                },
            'method': 'payments_status_update'
            }
        self.assertDictEqual(expected, json.loads(result.body))


    def test_payments_status_update_earned_app_currency(self):
        params = request_data.copy()
        details = order_details.copy()
        details['items'][0]['data'] = json.dumps(earned_app_currency)
        params.update(
            {
            'credits':{
                'order_details': json.dumps(details),
                'status': 'placed',
                'order_id': ORDER_ID
                }
            })

        params = {
            'signed_request': get_signed_request(**params),
            'order_details': json.dumps(details),
            'order_id': ORDER_ID,
            'method': 'payments_status_update',
            'status': 'placed',
            }

        result = self.app.post(
            '/%s/credits' % conf['facebook.namespace'],
            params,
            )

        expected = {
            'content': {
                'status': 'settled',
                'order_id': 987
                },
            'method': 'payments_status_update'
            }
        self.assertDictEqual(expected, json.loads(result.body))
