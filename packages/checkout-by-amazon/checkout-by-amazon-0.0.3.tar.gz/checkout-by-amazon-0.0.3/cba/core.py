import base64
import datetime
import hashlib, hmac
import logging
from lxml import etree, objectify
import requests
import urllib, urlparse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

action_details = {
    'CreatePurchaseContract': {
        'params': {
            'PurchaseContractMetadata': False,
            'DirectedId': True,
            'AuthorizationToken': True,
        },
        'response': ['PurchaseContractId'],
    },
    'GetPurchaseContract': {
        'params': {
            'PurchaseContractId': True,
        },
        'response': ['PurchaseContract'],
    },
    'SetPurchaseItems': {
        'params': {
            'PurchaseContractId': True,
        },
    },
    'SetContractCharges': {},
    'CompletePurchaseContract': {
        'params': {
            'PurchaseContractId': True,
            'IntegratorId': False,
            'IntegratorName': False,
            'InstantOrderProcessingNotificationURLs.MerchantUrl': False,
            'InstantOrderProcessingNotificationURLs.IntegratorURL': False,
        },
        'response': ['OrderIds.OrderId[:]'],
    },
}

def _dotted_getattr(obj, attr):
    left, _, right = attr.partition('.')
    if not right:
        return getattr(obj, right)
    else:
        return _dotted_getattr(getattr(obj, left), right)

def sign_request(method, host, request_uri='/', params={}, settings={}):
    keys = sorted(params.keys())
    params = [(key, params[key]) for key in keys]
    # cqs means Canonicalized Query String
    cqs = urllib.urlencode(params)
    to_sign = '\n'.join((method, host, request_uri, cqs))
    hash = hmac.new(settings['secret-access-key'], to_sign, hashlib.sha256)
    return base64.b64encode(hash.digest())

def make_request(method, action, params={}, settings={}):
    if action not in action_details:
        raise ValueError('Invalid action. Choose from {0}'.format(action_details.keys()))
    for ap, required in action_details[action]['params'].items():
        if required and ap not in params:
            raise ValueError('Missing required param "{0}"'.format(ap))
    if method not in ('GET', 'POST'):
        raise ValueError('method must be either "GET" or "POST"')
    host = 'payments{sandbox}.amazon.com'.format(sandbox=('-sandbox' if settings['sandbox'] else ''))
    endpoint = 'https://{host}/cba/api/purchasecontract/'.format(host=host)
    timestamp = datetime.datetime.utcnow()

    query = {
        'Action': action,
        'AWSAccessKeyId': settings['public-access-key'],
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': 2,
        'Timestamp': timestamp.isoformat(),
        'Version': '2010-08-31',
    }
    query.update(params)

    signature = sign_request(
        method,
        host,
        '/cba/api/purchasecontract/',
        query,
        settings=settings
    )
    query['Signature'] = signature

    logger.debug('{0} {1} with params={2}'.format(method, query['Action'], query))
    response = requests.request(method, endpoint, params=query)
    root = objectify.fromstring(response.content)
    if not hasattr(root, action + 'Result'):
        raise Exception('Bad response from Amazon!\n{0}'.format(etree.tostring(root, pretty_print=True)))
    result_element = getattr(root, action + 'Result')
    response_elements = tuple(eval('e.'+response, {}, {'e': result_element}) for response in action_details[action]['response'])
    request_id = root.ResponseMetadata.RequestId.text
    return response_elements, request_id
