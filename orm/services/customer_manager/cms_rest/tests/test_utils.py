import json

from wsme.exc import ClientSideError


def get_error(transaction_id, status_code, error_details=None,
              message=None):
    return ClientSideError(json.dumps({
        'code': status_code,
        'type': 'test',
        'created': '0.0',
        'transaction_id': transaction_id,
        'message': message if message else error_details,
        'details': 'test'
    }), status_code=status_code)
