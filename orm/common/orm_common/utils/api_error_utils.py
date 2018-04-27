import json
from orm.common.orm_common.utils import utils
from wsme.exc import ClientSideError


# This method creates a ClientSideError with given parameters
# and returns it to caller.
def get_error(transaction_id,
              error_details="",
              message=None,
              status_code=400):

    err = get_error_dict(status_code, transaction_id, message, error_details)
    return ClientSideError(json.dumps(err), status_code)


def get_error_dict(status_code, transaction_id, message, error_details=""):

    if not message:
        message = error_message[status_code]['message']

    # In case error like 409.1 we need to remove the dot part.
    status_code = int(status_code)

    return {
        'code': status_code,
        'type': error_message[status_code]['type'],
        'created': '{}'.format(utils.get_time_human()),
        'transaction_id': transaction_id,
        'message': message,
        'details': error_details
    }

# Default error messages
error_message = {
    400: {'message': 'Incompatible JSON body', 'type': 'Bad Request'},
    401: {'message': 'Unable to authenticate', 'type': 'Unauthorized'},
    403: {'message': 'Not allowed to perform this operation', 'type': 'Forbidden'},
    404: {'message': 'The specific transaction was not found', 'type': 'Not Found'},
    405: {'message': 'This method is not allowed', 'type': 'Method Not Allowed'},
    409: {'message': 'Current resource is busy', 'type': 'Conflict'},
    409.1: {'message': 'UUID already exists', 'type': 'Conflict'},
    409.2: {'message': 'Customer name already exists', 'type': 'Conflict'},
    500: {'message': 'Server error occurred', 'type': 'Internal Server Error'}
}
