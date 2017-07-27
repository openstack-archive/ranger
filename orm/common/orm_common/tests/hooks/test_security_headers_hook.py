import mock
from orm_common.hooks import security_headers_hook
from unittest import TestCase


class MyHeaders(object):
    def __init__(self):
        self.headers = {}

    def add(self, key, value):
        self.headers[key] = value


class TestSecurityHeadersHook(TestCase):
    def test_after(self):
        s = security_headers_hook.SecurityHeadersHook()
        test_headers = MyHeaders()
        state = mock.MagicMock()
        state.response.headers = test_headers
        s.after(state)

        security_headers = {'X-Frame-Options': 'DENY',
                            'X-Content-Type-Options': 'nosniff',
                            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                            'Content-Security-Policy': 'default-src \'self\'',
                            'X-Permitted-Cross-Domain-Policies': 'none',
                            'X-XSS-Protection': '1; mode=block'}

        for header in security_headers:
            self.assertEqual(security_headers[header],
                             test_headers.headers[header])
