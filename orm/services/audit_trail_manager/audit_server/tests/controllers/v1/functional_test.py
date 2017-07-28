"""functional_test module."""


from audit_server.tests.controllers.functional_test import FunctionalTest


class FunctionalTest(FunctionalTest):
    """base functional test class."""

    PATH_PREFIX = '/v1'
