"""Base classes for API tests.
"""

import pecan
import pecan.testing
import unittest
from pecan.testing import load_test_app
import os


class FunctionalTest(unittest.TestCase):
    """Used for functional tests of Pecan controllers.

    Used in case when you need to test your literal application and its
    integration with the framework.
    """

    PATH_PREFIX = ''

    def setUp(self):
        self.app = load_test_app(os.path.join(
            os.path.dirname(__file__),
            'config.py'
        ))

    def tearDown(self):
        super(FunctionalTest, self).tearDown()
        pecan.set_config({}, overwrite=True)

    def put_json(self, path, params, expect_errors=False, headers=None,
                 extra_environ=None, status=None):
        """Sends simulated HTTP PUT request to Pecan test app.

        :param path: url path of target service
        :param params: content for wsgi.input of request
        :param expect_errors: boolean value whether an error is expected based
                              on request
        :param headers: A dictionary of headers to send along with the request
        :param extra_environ: A dictionary of environ variables to send along
                              with the request
        :param status: Expected status code of response
        """
        return self.post_json(path=path, params=params,
                              expect_errors=expect_errors,
                              headers=headers, extra_environ=extra_environ,
                              status=status, method="put")

    def post_json(self, path, params, expect_errors=False, headers=None,
                  method="post", extra_environ=None, status=None):
        """Sends simulated HTTP POST request to Pecan test app.

        :param path: url path of target service
        :param params: content for wsgi.input of request
        :param expect_errors: boolean value whether an error is expected based
                              on request
        :param headers: A dictionary of headers to send along with the request
        :param method: Request method type. Appropriate method function call
                       should be used rather than passing attribute in.
        :param extra_environ: A dictionary of environ variables to send along
                              with the request
        :param status: Expected status code of response
        """
        full_path = self.PATH_PREFIX + path
        response = getattr(self.app, "%s_json" % method)(
            str(full_path),
            params=params,
            headers=headers,
            status=status,
            extra_environ=extra_environ,
            expect_errors=expect_errors
        )
        return response

    def delete(self, path, expect_errors=False, headers=None,
               extra_environ=None, status=None):
        """Sends simulated HTTP DELETE request to Pecan test app.

        :param path: url path of target service
        :param expect_errors: boolean value whether an error is expected based
                              on request
        :param headers: A dictionary of headers to send along with the request
        :param extra_environ: A dictionary of environ variables to send along
                              with the request
        :param status: Expected status code of response
        """
        full_path = self.PATH_PREFIX + path
        response = self.app.delete(str(full_path),
                                   headers=headers,
                                   status=status,
                                   extra_environ=extra_environ,
                                   expect_errors=expect_errors)
        return response

    def get_json(self, path, expect_errors=False, headers=None,
                 extra_environ=None, q=None, groupby=None, status=None,
                 override_params=None, **params):
        """Sends simulated HTTP GET request to Pecan test app.

        :param path: url path of target service
        :param expect_errors: boolean value whether an error is expected based
                              on request
        :param headers: A dictionary of headers to send along with the request
        :param extra_environ: A dictionary of environ variables to send along
                              with the request
        :param q: list of queries consisting of: field, value, op, and type
                  keys
        :param groupby: list of fields to group by
        :param status: Expected status code of response
        :param override_params: literally encoded query param string
        :param params: content for wsgi.input of request
        """
        q = q or []
        groupby = groupby or []
        full_path = self.PATH_PREFIX + path
        if override_params:
            all_params = override_params
        else:
            query_params = {'q.field': [],
                            'q.value': [],
                            'q.op': [],
                            'q.type': [],
                            }
            for query in q:
                for name in ['field', 'op', 'value', 'type']:
                    query_params['q.%s' % name].append(query.get(name, ''))
            all_params = {}
            all_params.update(params)
            if q:
                all_params.update(query_params)
            if groupby:
                all_params.update({'groupby': groupby})
        response = self.app.get(full_path,
                                params=all_params,
                                headers=headers,
                                extra_environ=extra_environ,
                                expect_errors=expect_errors,
                                status=status)
        if not expect_errors:
            response = response.json
        return response
