import urllib2

from urllib import quote

try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        try:
            from django.utils import simplejson as json
        except ImportError:
            raise ImportError('A json library is required to use ' + \
                             'this python library. Lol, yay for ' + \
                             'being verbose. ;)')

from .exceptions import *


class MailSnake(object):
    def __init__(self, apikey='', extra_params=None, api='api'):
        """
            Cache API key and address.
        """
        self.apikey = apikey
        self.api = api

        self.default_params = {'apikey': apikey}
        extra_params = extra_params or {}
        self.default_params.update(extra_params)

        if '-' in self.apikey:
            self.dc = self.apikey.split('-')[1]
        api_info = {
            'api':('api','1.3/?method='),
            'sts':('sts','1.0/'),
            'export':('api','export/1.0/')
        }
        self.api_url = 'https://%s.%s.mailchimp.com/%s' % \
                       ((self.dc,) + api_info[api])

    def call(self, method, params=None):
        url = self.api_url + method
        params = params or {}
        params.update(self.default_params)

        if self.api == 'api':
            post_data = urllib2.quote(json.dumps(params))
            headers = {'Content-Type':'application/json'}
        else:
            headers = {'Content-Type':
                      'application/x-www-form-urlencoded'}
            post_data = http_build_query(params)
            if self.api == 'sts':
                url += '.json/'
            else:
                # Use GET for the Export API
                url += '?' + post_data
                post_data = ''
        request = urllib2.Request(url, post_data, headers)

        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            raise NetworkTimeoutException(str(e.reason))
        except urllib2.HTTPError, e:
            raise HTTPRequestException(e.code)

        try:
            if self.api == 'export':
                rsp = [json.loads(i) for i in response.readlines()]
            else:
                rsp = json.loads(response.read())
        except json.JSONDecodeError, e:
            raise ParseException(e.message)

        if not isinstance(rsp, (int, bool, basestring)) and \
                'error' in rsp and 'code' in rsp:
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

##################################################
# http://www.codigomanso.com/en/2010/04/http_build_query-para-python/
# By Pau Sanchez
# Mimics the behaviour of http_build_query PHP function
# This method can be useful for sending data to flash applications
##################################################
def http_build_query(params, topkey = ''): 
    if len(params) == 0:
        return ''

    result = ''
 
    # is a dictionary?
    if type (params) is dict:
        for key in params.keys():
            newkey = quote(key)
            if topkey != '':
                newkey = topkey + quote('[' + key + ']')
 
            if type(params[key]) is dict:
                result += http_build_query(params[key], newkey)
            elif type(params[key]) is list:
                i = 0
                for val in params[key]:
                    result += newkey + quote('[' + str(i) + ']') + \
                              '=' + quote(str(val)) + '&'
                    i = i + 1
            # boolean should have special treatment as well
            elif type(params[key]) is bool:
                result += newkey + '=' + \
                          quote(str(int(params[key]))) + '&'
            # assume string (integers and floats work well)
            else:
                result += str(newkey) + '=' + quote(str(params[key])) + '&'

    # remove the last '&'
    if (result) and (topkey == '') and (result[-1] == '&'):
        result = result[:-1]

    return result
