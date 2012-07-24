import unittest
from stackato import restclient


class MockRestClient(restclient.RestClient):
    class requests(object):
        @classmethod
        def session(cls, headers, verify):
            cls.init = [headers, verify]
            return cls

        headers = {}

        @classmethod
        def request(cls, method, url, return_response=False):
            return cls.request_obj

        class request_obj(object):
            headers = {'Content-Type': ''}

            @classmethod
            def send(cls, prefetch):
                pass
            response = None


class RestClientTests(unittest.TestCase):
    def test_init(self):
        client = MockRestClient()
        self.assertEqual(client.requests.init,
                         [{'Pragma': 'no-cache', 'Cache-Control': 'no-cache'},
                          False])

    def test_target(self):
        client = MockRestClient()
        self.assertEqual(client.target, 'https://api.127.0.0.1.xip.io')

    def test_headers(self):
        client = MockRestClient()
        self.assertEqual(client.headers, {})

    def test_request(self):
        client = MockRestClient()
        client.request('foo', 'bar')


class ExceptionsTests(unittest.TestCase):
    def test_it(self):
        from stackato import exceptions


class StackatoClientTests(unittest.TestCase):
    def test_it(self):
        from stackato import stackatoclient
