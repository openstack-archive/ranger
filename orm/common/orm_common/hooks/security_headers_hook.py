import logging

from pecan.hooks import PecanHook

logger = logging.getLogger(__name__)


class SecurityHeadersHook(PecanHook):
    def after(self, state):
        security_headers = {'X-Frame-Options': 'DENY',
                            'X-Content-Type-Options': 'nosniff',
                            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                            'Content-Security-Policy': 'default-src \'self\'',
                            'X-Permitted-Cross-Domain-Policies': 'none',
                            'X-XSS-Protection': '1; mode=block'}

        # Add all the security headers
        for header, value in security_headers.items():
            state.response.headers.add(header, value)
