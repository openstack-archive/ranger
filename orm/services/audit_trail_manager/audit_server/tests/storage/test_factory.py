"""test_factory module."""

import unittest

from audit_server.storage import factory
from audit_server.storage.mysql.transaction import Connection
from mock import patch
from sqlalchemy import create_engine


class Test(unittest.TestCase):
    """test factory class."""

    @patch.object(create_engine, '__init__')
    def test_get_get_transaction_connection(self, mock_engine):
        """test get_zone_resource_type_status.

        test that get_zone_resource_type_status_connection returns
        an instance of type ZoneResourceTypeStatusConnection.
        """
        factory.database_url = 'mysql://root:stack@127.0.0.1/orm_audit?' \
                               'charset=utf8'
        factory.echo_statements = False
        mock_engine.get_session.return_value = None
        conn = factory.get_transaction_connection()
        self.assertIsInstance(conn, Connection)
