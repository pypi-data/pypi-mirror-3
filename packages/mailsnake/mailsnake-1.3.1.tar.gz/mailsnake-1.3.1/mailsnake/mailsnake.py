import urllib2

try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        try:
            from django.utils import simplejson as json
        except ImportError:
            raise ImportError('A json library is required to use this python library. Lol, yay for being verbose. ;)')

from exceptions import *


class MailSnake(object):
    def __init__(self, apikey='', extra_params=None):
        """
            Cache API key and address.
        """
        self.apikey = apikey

        self.default_params = {'apikey': apikey}
        extra_params = extra_params or {}
        self.default_params.update(extra_params)

        dc = 'us1'
        if '-' in self.apikey:
            dc = self.apikey.split('-')[1]
        self.base_api_url = 'https://%s.api.mailchimp.com/1.3/?method=' % dc

    def call(self, method, params=None):
        url = self.base_api_url + method
        params = params or {}
        params.update(self.default_params)

        post_data = urllib2.quote(json.dumps(params))
        headers = {'Content-Type': 'application/json'}
        request = urllib2.Request(url, post_data, headers)

        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            raise NetworkTimeoutException(e.reason)
        except urllib2.HTTPError, e:
            raise HTTPRequestException(e.reason)

        try:
            rsp = json.loads(response.read())
        except json.JSONDecodeError, e:
            raise ParseException(e.reason)

        if 'error' in rsp and 'code' in rsp:
            try:
                Err = exception_for_code(rsp['code'])
            except KeyError:
                raise SystemException(rsp['error'])
            raise Err(rsp['error'])

        return rsp

    def __getattr__(self, method_name):

        def get(self, *args, **kwargs):
            params = dict((i, j) for (i, j) in enumerate(args))
            params.update(kwargs)
            return self.call(method_name, params)

        return get.__get__(self)
