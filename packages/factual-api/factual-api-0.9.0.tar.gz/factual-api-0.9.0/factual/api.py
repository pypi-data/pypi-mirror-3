"""
Factual API driver
"""

import json
from urllib import urlencode

import requests
from oauth_hook import OAuthHook

from query import Crosswalk, Resolve, Table

API_V3_HOST = "http://api.v3.factual.com"
DRIVER_VERSION_TAG = "factual-python-driver-1.0"

class Factual(object):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.api = API(self._generate_token(key, secret))

    def table(self, table):
        return Table(self.api, 't/' + table)

    def crosswalk(self):
        return Crosswalk(self.api)

    def resolve(self, values):
        return Resolve(self.api, values)

    def _generate_token(self, key, secret):
        access_token = OAuthHook(consumer_key=key, consumer_secret=secret, header_auth=True)
        return access_token


class API(object):
    def __init__(self, access_token):
        self.client = requests.session(hooks={'pre_request': access_token})

    def execute(self, query):
        response = self._handle_request(query.path, query.params)
        return response
        
    def schema(self, query):
        response = self._handle_request(query.path + '/schema', query.params)
        return response['view']

    def build_url(self, path, params):
        url = API_V3_HOST + '/' + path + '?' + self._make_query_string(params)
        return url

    def _handle_request(self, path, params):
        response = self._make_request(path, params)
        payload = json.loads(response)
        if payload['status'] != 'ok':
            raise APIException(payload['error_type'] + ' - ' + payload['message'])
        return payload['response']
        
    def _make_request(self, path, params):
        # _make_query_string can be removed when when an issue in requests-oauth
        # that drops params gets fixed
        url = self.build_url(path, params)
        headers = {'X-Factual-Lib': DRIVER_VERSION_TAG}
        response = self.client.get(url, headers=headers)
        return response.text

    def _make_query_string(self, params):
        string_params = []
        for key, val in params.items():
            transformed = json.dumps(val) if not isinstance(val, str) else val
            string_params.append((key, transformed))
        return urlencode(string_params)


class APIException(Exception):
    pass
