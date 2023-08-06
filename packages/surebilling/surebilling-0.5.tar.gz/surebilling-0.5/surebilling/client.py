from datetime import datetime
from decimal import Decimal
import json
import urllib
import urllib2
import logging

log = logging.getLogger('surebilling')

def http_post(url, args = {}):
#    print 'POSTing to ', url, args
    return urllib2.urlopen(url, urllib.urlencode(args)).read()

API_SERVER = 'http://test.flow.com:8001'

try:
    from django.conf import settings
    API_SERVER = settings.SUREBILLING_API_SERVER
except (ImportError, AttributeError):
    pass

def api_serialize(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    raise Exception("Unsupported type %s: %s", type(obj), str(obj))

class BillingException(Exception):
    pass

class Client(object):
    def __init__(self, apikey):
        self.apikey = apikey

    def call(self, function, **kw):
        try:
            data = json.loads(http_post('%s/api/%s/' % (API_SERVER, function), dict(apikey = self.apikey, json = json.dumps(kw, default = api_serialize))))
        except urllib2.HTTPError, e:
            log.exception(e.fp.read())
            raise e

        if data['status'] != 0:
            raise BillingException("Server returned status %d: %s" % (data['status'], data['data']))
        return data['data']

    def recurring_add(self, **kw):
        return self.call('recurring_add', **kw)

    def recurring_get(self, **kw):
        return self.call('recurring_get', **kw)

    def recurring_list(self, **kw):
        return self.call('recurring_list', **kw)

    def recurring_delete(self, id):
        return self.call('recurring_delete', id = id)

    def invoice_add(self, **kw):
        return self.call('invoice_add', **kw)

    def invoice_delete(self, id):
        return self.call('invoice_delete', id = id)

    def customer_add(self, **kw):
        return self.call('customer_add', **kw)

    def customer_get(self, id):
        return self.call('customer_get', id = id)

    def customer_update(self, **kw):
        return self.call('customer_update', **kw)

    def customer_delete(self, **kw):
        return self.call('customer_delete', **kw)

    def customer_balance(self, **kw):
        return self.call('customer_balance', **kw)

    def customer_balance_multi(self, **kw):
        return self.call('customer_balance_multi', **kw)

    def sso_token(self, **kw):
        return self.call('sso_token', **kw)

