# coding: utf-8
import urllib
from hashlib import md5
from functools import partial
from smartresponder import http

try:
    import json
except ImportError:
    import simplejson as json

DEFAULT_TIMEOUT = 1
API_URL = 'http://api.smartresponder.ru/'
REQUEST_ENCODING = 'utf8'

# See full list of VK API methods here: http://api.smartresponder.ru/doc/
COMPLEX_METHODS = ['main', 'deliveries', 'files', 'templates', 'subscribers',
                   'subscribe', 'groups', 'tracks', 'catalog']

class SMRError(Exception):
    __slots__ = ["error"]

    def __init__(self, error_data):
        self.error = error_data
        Exception.__init__(self, str(self))

    @property
    def code(self):
        return self.error['error_code']

    @property
    def description(self):
        return self.error['error_msg']

    @property
    def params(self):
        return self.error['request_params']

    def __unicode__(self):
        return "Error(code = '%s', description = '%s', params = '%s')" % (self.code, self.description, self.params)

    def __str__(self):
        return "Error(code = '%s', params = '%s')" % (self.code, self.params)


def safe_json_loads(data):
    return json.loads(data[data.find('{'):])


def _encode(s):
    if isinstance(s, (dict, list, tuple)):
        s = json.dumps(s, ensure_ascii=False, encoding=REQUEST_ENCODING)

    if isinstance(s, unicode):
        s = s.encode(REQUEST_ENCODING)

    return s # this can be number, etc.


def signature(api_secret, params):
    if isinstance(params, dict):
        params = params.items()
    param_str = ":".join(
        ["%s=%s" % (str(key), _encode(value)) for key, value in params] +
        ["%s=%s" % ('password', api_secret)])
    return md5(param_str).hexdigest()


class _API(object):
    def __init__(self, api_id=None, api_secret=None, token=None, **defaults):
        if not (api_id and api_secret or token):
            raise ValueError("Arguments api_id and api_secret or token are required")

        self.api_id = api_id
        self.api_secret = api_secret
        self.token = token
        self.defaults = defaults

    def __call__(self, **kwargs):
        scope = kwargs.pop('scope', None) or getattr(self, 'scope')
        params = self.defaults.copy()
        params.update(kwargs)
        return self._get(scope, **params)

    def _signature(self, params):
        return signature(self.api_secret, params)

    def _get(self, method, timeout=DEFAULT_TIMEOUT, **kwargs):
        status, response = self._request(method, timeout=timeout, **kwargs)
        if not (200 <= status <= 299):
            raise SMRError({
                'error_code': status,
                'error_msg': "HTTP error",
                'request_params': kwargs,
                })

        data = json.loads(response, strict=False)
        if "error" in data:
            raise SMRError({
                'error_code': data['error']['code'],
                'error_msg': data['error']['message'],
                'request_params': kwargs,
                })
        return data

    def __getattr__(self, name):
        '''
        Support for api.<method>.<methodName> syntax
        '''
        if name in COMPLEX_METHODS:
            api = _API(api_id=self.api_id, api_secret=self.api_secret, token=self.token, **self.defaults)
            api.scope = name
            return api

        # the magic to convert instance attributes into method names
        return partial(self, action=name)

    def _request(self, scope, timeout=DEFAULT_TIMEOUT, **kwargs):
        for key, value in kwargs.iteritems():
            kwargs[key] = _encode(value)

        params = {
            'format': 'json',
            }
        params.update(kwargs)
        params_list = params.items()

        if self.token:
            params_list += [('api_key', self.token)]
        else:
            params_list += [('api_id', self.api_id)]
            sig = self._signature(params_list)
            params_list += [('hash', sig)]

        data = urllib.urlencode(params_list)
        url = API_URL + scope + '.html'
        secure = False

        headers = {"Accept": "application/json",
                   "Content-Type": "application/x-www-form-urlencoded"}
        return http.post(url, data, headers, timeout, secure=secure)


class API(_API):
    def get(self, method, timeout=DEFAULT_TIMEOUT, **kwargs):
        return self._get(method, timeout, **kwargs)