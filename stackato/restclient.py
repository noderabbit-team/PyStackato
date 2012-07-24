# -*- coding: utf-8 -*-

import requests

try:
    import simplejson as json
except ImportError:
    import json


class RestClient(object):
    """
    The RestClient class attempts to be a generic HTTP REST client interface,
    sitting on top of the `requests` library session class (allowing for,
    among other things, a singular HTTP connection across all requests). A
    base url is stored, with all further requests being paths that are
    appended to this base. SSL certificates are not verified, and caching is
    disabled, by default.
    """

    requests = requests

    def __init__(self, baseurl=None, **kwargs):
        headers = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
        headers.update(kwargs.pop('headers', {}))
        verify_ssl = kwargs.pop('verify', False)

        self.config = kwargs.copy()
        self.requester = self.requests.session(
            verify=verify_ssl, headers=headers, **kwargs)
        self.target = baseurl

    @property
    def target(self):
        return "%s://%s" % (self.__protocol, self.__baseurl)

    @target.setter
    def target(self, baseurl):
        if not isinstance(baseurl, str):
            baseurl = 'https://api.127.0.0.1.xip.io'
        if '://' in baseurl:
            self.__protocol, self.__baseurl = baseurl.split('://')
        else:
            self.__protocol = 'https'
            self.__baseurl = baseurl

    @property
    def headers(self):
        return self.requester.headers.copy()

    @headers.setter
    def headers(self, value):
        self.requester.headers = dict(value)

    def request(self, method, path, **kwargs):
        url = "%s%s" % (self.target, path)
        return_response = kwargs.pop('return_response', True)

        request = self.requester.request(method, url, return_response=False, **kwargs)

        content_type = request.headers['Content-Type']
        if content_type and 'application/json' in content_type:
            data = request.data
            request.data = json.dumps(data)

        if return_response:
            request.send(prefetch=True)
            response = request.response
            # response.raise_for_status()
            return response
        else:
            return request

    def head(self, path, **kwargs):
        return self.request('head', path, **kwargs)

    def options(self, path, **kwargs):
        return self.request('options', path, **kwargs)

    def get(self, path, **kwargs):
        return self.request('get', path, **kwargs)

    def put(self, path, **kwargs):
        return self.request('put', path, **kwargs)

    def post(self, path, **kwargs):
        return self.request('post', path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request('delete', path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request('patch', path, **kwargs)

    def __repr__(self):
        return '<RestClient [%s]>' % (self.target)
