"""factory module."""


from orm.services.audit_trail_manager.audit_server.storage.mysql.transaction import Connection as Transaction

database_url = 'NA'
echo_statements = False


def get_transaction_connection():
    """return a transaction orm implementation."""
    return Transaction(database_url, echo_statements)
